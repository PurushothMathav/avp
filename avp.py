import os
import subprocess
import json
import shutil
import threading
import multiprocessing
import time
from datetime import datetime
from tqdm import tqdm
import colorama
from colorama import Fore, Style, Back
from tabulate import tabulate
import platform
import psutil

# Initialize colorama for cross-platform colored terminal output
colorama.init(autoreset=True)

# Configuration
INPUT_FOLDER = "videos"  # <-- change if needed
NUM_THREADS = max(1, multiprocessing.cpu_count() - 2)  # Automatically set based on CPU
REPORT_FILE = "video_processing_report.txt"

# Global stats tracking
stats = {
    "total_files": 0,
    "processed_files": 0,
    "mkv_converted": 0,
    "subtitles_extracted": 0,
    "audio_fixed": 0,
    "errors": [],
    "start_time": None,
    "end_time": None,
    "file_details": []
}

# For thread-safe updating of stats
stats_lock = threading.Lock()

def print_banner():
    """Prints a professional banner for the application"""
    os.system('cls' if os.name == 'nt' else 'clear')
    banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗
{Fore.CYAN}║ {Style.BRIGHT}{Fore.WHITE}                Advanced Video Processor                  {Fore.CYAN}║
{Fore.CYAN}╠══════════════════════════════════════════════════════════════╣
{Fore.CYAN}║ {Fore.WHITE}• Converts MKV to MP4         • Extracts subtitles         {Fore.CYAN}║
{Fore.CYAN}║ {Fore.WHITE}• Fixes audio codecs          • Multi-threaded processing  {Fore.CYAN}║
{Fore.CYAN}╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)
    
    # System info
    system = platform.system()
    cpu = platform.processor()
    ram = round(psutil.virtual_memory().total / (1024**3), 2)
    
    print(f"{Fore.YELLOW}System Information:")
    print(f"{Fore.WHITE}• OS: {system}")
    print(f"{Fore.WHITE}• CPU: {cpu}")
    print(f"{Fore.WHITE}• RAM: {ram} GB")
    print(f"{Fore.WHITE}• Threads: {NUM_THREADS}")
    
    print(f"\n{Fore.GREEN}Starting process with folder: {Fore.WHITE}{INPUT_FOLDER}\n")

def get_audio_codec(file_path):
    """Run ffprobe and check audio codec"""
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "a:0",
        "-show_entries", "stream=codec_name",
        "-of", "json",
        file_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        info = json.loads(result.stdout)
        codec = info['streams'][0]['codec_name']
        return codec
    except (KeyError, IndexError, json.JSONDecodeError):
        return None

def get_video_info(file_path):
    """Get complete video information"""
    info = {"duration": None, "resolution": None, "video_codec": None, "size_mb": None}
    
    # Get file size
    try:
        info["size_mb"] = round(os.path.getsize(file_path) / (1024 * 1024), 2)
    except:
        pass
    
    # Get video information
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,codec_name",
        "-show_entries", "format=duration",
        "-of", "json",
        file_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)
        
        # Get duration
        if 'format' in data and 'duration' in data['format']:
            duration_sec = float(data['format']['duration'])
            mins = int(duration_sec // 60)
            secs = int(duration_sec % 60)
            info["duration"] = f"{mins}:{secs:02d}"
            
        # Get resolution and codec
        if 'streams' in data and len(data['streams']) > 0:
            stream = data['streams'][0]
            if 'width' in stream and 'height' in stream:
                info["resolution"] = f"{stream['width']}x{stream['height']}"
            if 'codec_name' in stream:
                info["video_codec"] = stream['codec_name']
                
    except Exception as e:
        pass
        
    return info

def extract_subtitles(file_path):
    """Extract subtitles from video file"""
    base_name = os.path.splitext(file_path)[0]
    srt_path = f"{base_name}.srt"
    
    # Check if the file has subtitles
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "s",
        "-show_entries", "stream=index",
        "-of", "json",
        file_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        info = json.loads(result.stdout)
        
        # If subtitles exist, extract them
        if 'streams' in info and len(info['streams']) > 0:
            # Extract the first subtitle stream (index 0)
            subprocess.run([
                "ffmpeg", "-y", "-i", file_path,
                "-map", "0:s:0", srt_path
            ], capture_output=True)
            
            with stats_lock:
                stats["subtitles_extracted"] += 1
                
            return True
        else:
            return False
    except Exception as e:
        with stats_lock:
            stats["errors"].append(f"Subtitle extraction error on {os.path.basename(file_path)}: {str(e)}")
        return False

def convert_mkv_to_mp4(mkv_path):
    """Convert MKV to MP4 with subtitle preservation"""
    mp4_path = os.path.splitext(mkv_path)[0] + ".mp4"
    
    try:
        process = subprocess.run([
            "ffmpeg", "-y", "-i", mkv_path,
            "-map", "0", "-c:v", "copy", "-c:a", "copy", "-c:s", "mov_text",
            mp4_path
        ], capture_output=True)
        
        if os.path.exists(mp4_path):
            with stats_lock:
                stats["mkv_converted"] += 1
            return mp4_path
        else:
            with stats_lock:
                stats["errors"].append(f"Failed to convert {os.path.basename(mkv_path)}")
            return mkv_path
    except Exception as e:
        with stats_lock:
            stats["errors"].append(f"MKV conversion error on {os.path.basename(mkv_path)}: {str(e)}")
        return mkv_path

def fix_audio(file_path):
    """Fix audio if necessary"""
    base_name = os.path.splitext(file_path)[0]
    video_only = f"{base_name}_video.mp4"
    audio_fixed = f"{base_name}_audio.aac"
    final_output = f"{base_name}_fixed.mp4"

    try:
        # Extract video only
        subprocess.run([
            "ffmpeg", "-y", "-i", file_path, "-c:v", "copy", "-an", video_only
        ], capture_output=True)

        # Extract and re-encode audio to AAC
        subprocess.run([
            "ffmpeg", "-y", "-i", file_path, "-vn", "-c:a", "aac", "-b:a", "192k", audio_fixed 
        ], capture_output=True)

        # Mux video and audio together
        subprocess.run([
            "ffmpeg", "-y", "-i", video_only, "-i", audio_fixed, "-c:v", "copy", "-c:a", "copy", final_output
        ], capture_output=True)

        # Cleanup temp files
        if os.path.exists(video_only):
            os.remove(video_only)
        if os.path.exists(audio_fixed):
            os.remove(audio_fixed)

        with stats_lock:
            stats["audio_fixed"] += 1
            
        return True
    except Exception as e:
        with stats_lock:
            stats["errors"].append(f"Audio fix error on {os.path.basename(file_path)}: {str(e)}")
        return False

def worker(file_list, thread_id):
    """Worker function for threading"""
    for filename in file_list:
        file_path = os.path.join(INPUT_FOLDER, filename)
        original_path = file_path
        file_details = {
            "filename": filename,
            "original_size": None,
            "final_size": None,
            "duration": None,
            "resolution": None,
            "original_codec": None,
            "has_subtitles": False,
            "actions": []
        }
        
        # Get initial file information
        info = get_video_info(file_path)
        file_details["original_size"] = info["size_mb"]
        file_details["duration"] = info["duration"]
        file_details["resolution"] = info["resolution"]
        file_details["original_codec"] = info["video_codec"]
        
        # Process information string for progress bar
        action_str = f"Thread {thread_id} | {filename}"
        
        # If MKV, first convert to MP4
        if filename.lower().endswith('.mkv'):
            print(f"{Fore.BLUE}🎞️ Converting: {Fore.WHITE}{filename}")
            mp4_path = convert_mkv_to_mp4(file_path)
            file_path = mp4_path  # Work on the newly created MP4
            file_details["actions"].append("MKV converted to MP4")

        # Extract subtitles if available
        print(f"{Fore.MAGENTA}📝 Checking subtitles: {Fore.WHITE}{filename}")
        has_subs = extract_subtitles(file_path)
        file_details["has_subtitles"] = has_subs
        if has_subs:
            file_details["actions"].append("Subtitles extracted")

        # Now check and fix audio
        codec = get_audio_codec(file_path)
        file_details["audio_codec"] = codec

        if codec is None:
            print(f"{Fore.RED}⚠️ No audio stream: {Fore.WHITE}{filename}")
            file_details["actions"].append("No audio stream detected")
        elif codec.lower() == "aac":
            print(f"{Fore.GREEN}✓ Audio codec (AAC): {Fore.WHITE}{filename}")
            file_details["actions"].append("Audio already in AAC format")
        else:
            print(f"{Fore.YELLOW}🔧 Fixing audio ({codec}): {Fore.WHITE}{filename}")
            fix_audio(file_path)
            file_details["actions"].append(f"Audio converted from {codec} to AAC")
        
        # Get final file information if different from original
        if original_path != file_path and os.path.exists(file_path):
            info = get_video_info(file_path)
            file_details["final_size"] = info["size_mb"]
        else:
            file_details["final_size"] = file_details["original_size"]
        
        # Update stats
        with stats_lock:
            stats["processed_files"] += 1
            stats["file_details"].append(file_details)
            
            # Update progress display
            progress = (stats["processed_files"] / stats["total_files"]) * 100
            bar_length = 40
            filled_length = int(bar_length * stats["processed_files"] // stats["total_files"])
            
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            
            print(f"\r{Fore.CYAN}Progress: {Fore.WHITE}{bar} {Fore.YELLOW}{progress:.1f}% {Fore.WHITE}({stats['processed_files']}/{stats['total_files']})", end='')

def format_time(seconds):
    """Format seconds into hours, minutes, seconds"""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"

def generate_report():
    """Generate and display final processing report"""
    # Calculate elapsed time
    total_time = (stats["end_time"] - stats["start_time"]).total_seconds()
    
    # Clear screen and show report
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print(f"\n{Back.BLUE}{Fore.WHITE}{Style.BRIGHT} VIDEO PROCESSING REPORT {Style.RESET_ALL}")
    print(f"\n{Fore.CYAN}📊 SUMMARY STATISTICS")
    print(f"{Fore.WHITE}{'━' * 50}")
    
    print(f"{Fore.YELLOW}• Total Files Processed: {Fore.WHITE}{stats['processed_files']}")
    print(f"{Fore.YELLOW}• MKV Files Converted: {Fore.WHITE}{stats['mkv_converted']}")
    print(f"{Fore.YELLOW}• Subtitles Extracted: {Fore.WHITE}{stats['subtitles_extracted']}")
    print(f"{Fore.YELLOW}• Audio Tracks Fixed: {Fore.WHITE}{stats['audio_fixed']}")
    print(f"{Fore.YELLOW}• Total Processing Time: {Fore.WHITE}{format_time(total_time)}")
    
    # Calculate success rate
    success_rate = 100 - (len(stats["errors"]) / max(1, stats["total_files"]) * 100)
    print(f"{Fore.YELLOW}• Success Rate: {Fore.GREEN}{success_rate:.1f}%")
    
    # Show any errors
    if stats["errors"]:
        print(f"\n{Fore.RED}⚠️ ERRORS {Fore.WHITE}({len(stats['errors'])})")
        print(f"{Fore.WHITE}{'━' * 50}")
        for i, error in enumerate(stats["errors"][:5], 1):  # Show first 5 errors
            print(f"{i}. {error}")
        
        if len(stats["errors"]) > 5:
            print(f"...and {len(stats['errors']) - 5} more errors (see report file)")
    
    # File details table
    print(f"\n{Fore.CYAN}📋 FILE DETAILS")
    print(f"{Fore.WHITE}{'━' * 50}")
    
    # Prepare table data
    table_data = []
    for file in stats["file_details"]:
        # Calculate size change if applicable
        size_diff = ""
        if file["original_size"] and file["final_size"] and file["original_size"] != file["final_size"]:
            change = ((file["final_size"] - file["original_size"]) / file["original_size"]) * 100
            size_diff = f"{change:+.1f}%"
        
        # Summarize actions
        actions = ", ".join(file["actions"]) if file["actions"] else "No action needed"
        
        # Add row to table
        table_data.append([
            file["filename"][:20] + "..." if len(file["filename"]) > 23 else file["filename"],
            file["resolution"] or "N/A",
            file["duration"] or "N/A",
            f"{file['original_size']} MB" if file["original_size"] else "N/A",
            f"{file['final_size']} MB {size_diff}" if file["final_size"] else "N/A",
            actions[:30] + "..." if len(actions) > 33 else actions
        ])
    
    # Print table (limit to 10 rows for display)
    headers = ["Filename", "Resolution", "Duration", "Original", "Final Size", "Actions"]
    if table_data:
        print(tabulate(table_data[:10], headers=headers, tablefmt="pretty"))
        if len(table_data) > 10:
            print(f"...and {len(table_data) - 10} more files (see report file)")
    
    # Save detailed report to file
    with open(REPORT_FILE, "w") as f:
        # Write header
        f.write("VIDEO PROCESSING REPORT\n")
        f.write("======================\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Processing Time: {format_time(total_time)}\n\n")
        
        # Write summary
        f.write("SUMMARY STATISTICS\n")
        f.write("-----------------\n")
        f.write(f"Total Files Processed: {stats['processed_files']}\n")
        f.write(f"MKV Files Converted: {stats['mkv_converted']}\n")
        f.write(f"Subtitles Extracted: {stats['subtitles_extracted']}\n")
        f.write(f"Audio Tracks Fixed: {stats['audio_fixed']}\n")
        f.write(f"Success Rate: {success_rate:.1f}%\n\n")
        
        # Write file details
        f.write("FILE DETAILS\n")
        f.write("-----------\n")
        
        for file in stats["file_details"]:
            f.write(f"Filename: {file['filename']}\n")
            f.write(f"Resolution: {file['resolution'] or 'N/A'}\n")
            f.write(f"Duration: {file['duration'] or 'N/A'}\n")
            f.write(f"Original Size: {file['original_size']} MB\n" if file["original_size"] else "Original Size: N/A\n")
            f.write(f"Final Size: {file['final_size']} MB\n" if file["final_size"] else "Final Size: N/A\n")
            f.write(f"Has Subtitles: {'Yes' if file['has_subtitles'] else 'No'}\n")
            f.write(f"Actions Performed: {', '.join(file['actions']) if file['actions'] else 'No action needed'}\n")
            f.write("\n")
        
        # Write errors
        if stats["errors"]:
            f.write("ERRORS\n")
            f.write("------\n")
            for i, error in enumerate(stats["errors"], 1):
                f.write(f"{i}. {error}\n")
    
    print(f"\n{Fore.GREEN}✅ Detailed report saved to: {Fore.WHITE}{REPORT_FILE}")

def main():
    """Main processing function"""
    print_banner()
    
    # Get list of files
    if not os.path.exists(INPUT_FOLDER):
        os.makedirs(INPUT_FOLDER)
        print(f"{Fore.YELLOW}Created input folder: {INPUT_FOLDER}")
    
    filenames = [f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith(('.mp4', '.mkv'))]
    
    if not filenames:
        print(f"{Fore.RED}No video files found in the input folder!")
        return
    
    # Start timing and initialize stats
    stats["start_time"] = datetime.now()
    stats["total_files"] = len(filenames)
    
    print(f"{Fore.GREEN}Found {Fore.WHITE}{len(filenames)}{Fore.GREEN} video files to process")
    print(f"{Fore.WHITE}{'─' * 50}")
    
    # Split files among threads
    chunks = [filenames[i::NUM_THREADS] for i in range(NUM_THREADS)]
    threads = []

    for i, chunk in enumerate(chunks):
        thread = threading.Thread(target=worker, args=(chunk, i+1))
        thread.start()
        threads.append(thread)

    # Display processing animation
    try:
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Process interrupted by user.")
    
    # Calculate end time
    stats["end_time"] = datetime.now()
    
    # Print final report
    print("\n\n")
    generate_report()

if __name__ == "__main__":
    main()
