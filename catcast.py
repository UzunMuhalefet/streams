import json
import os
import requests
from pathlib import Path

def load_config(config_file="catcast-config.json"):
    """Load configuration from JSON file."""
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_current_program(channel_id):
    """Send POST request to get current program information."""
    url = f"https://api.catcast.tv/api/channels/{channel_id}/getcurrentprogram"
    
    try:
        response = requests.post(url, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for channel {channel_id}: {e}")
        return None

def create_m3u8_file(slug, stream_url, output_dir="catcast"):
    """Create M3U8 playlist file."""
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Create M3U8 content
    m3u8_content = f"""#EXTM3U
#EXT-X-VERSION:3
#EXT-X-STREAM-INF:BANDWIDTH=2000000
{stream_url}
"""
    
    # Write to file
    output_file = os.path.join(output_dir, f"{slug}.m3u8")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(m3u8_content)
    
    print(f"✓ Created M3U8 file: {output_file}")
    return output_file

def delete_m3u8_file(slug, output_dir="catcast"):
    """Delete M3U8 playlist file if it exists."""
    output_file = os.path.join(output_dir, f"{slug}.m3u8")
    
    if os.path.exists(output_file):
        try:
            os.remove(output_file)
            print(f"✗ Deleted M3U8 file: {output_file}")
            return True
        except Exception as e:
            print(f"Error deleting file {output_file}: {e}")
            return False
    else:
        print(f"✗ File not found (already deleted or never created): {output_file}")
        return False

def main():
    """Main function to process all channels."""
    # Load configuration
    try:
        config = load_config()
    except FileNotFoundError:
        print("Error: catcast-config.json not found")
        return
    except json.JSONDecodeError:
        print("Error: Invalid JSON in catcast-config.json")
        return
    
    successful_channels = []
    failed_channels = []
    
    # Process each channel
    for channel in config:
        channel_id = channel.get("id")
        slug = channel.get("slug")
        
        if not channel_id or not slug:
            print(f"Skipping invalid channel entry: {channel}")
            continue
        
        print(f"\nProcessing channel: {slug} (ID: {channel_id})")
        
        # Get current program data
        response_data = get_current_program(channel_id)
        
        if not response_data:
            print(f"Failed to get data for channel {channel_id}")
            delete_m3u8_file(slug)
            failed_channels.append(slug)
            continue
        
        # Extract full_mobile_url
        if response_data.get("status") == 1 and "data" in response_data:
            data = response_data["data"]
            full_mobile_url = data.get("full_mobile_url")
            
            if full_mobile_url:
                # Create M3U8 file
                create_m3u8_file(slug, full_mobile_url)
                successful_channels.append(slug)
                print(f"Successfully processed {slug}")
            else:
                print(f"No full_mobile_url found for channel {channel_id}")
                delete_m3u8_file(slug)
                failed_channels.append(slug)
        else:
            print(f"Invalid response status for channel {channel_id}")
            delete_m3u8_file(slug)
            failed_channels.append(slug)
    
    # Summary
    print("\n" + "="*50)
    print("Processing Summary:")
    print("="*50)
    print(f"✓ Successful: {len(successful_channels)} channels")
    if successful_channels:
        for slug in successful_channels:
            print(f"  - {slug}")
    
    print(f"\n✗ Failed: {len(failed_channels)} channels")
    if failed_channels:
        for slug in failed_channels:
            print(f"  - {slug}")
    
    print("\nProcessing complete!")

if __name__ == "__main__":
    main()
