"""
═══════════════════════════════════════════════════════════════════════════
                          INSTAGRAM_SCRAPER.PY
       INSTAGRAM POST SCRAPER - DOWNLOADS LATEST POSTS FROM INSTAGRAM
             PROFILES USING INSTALOADER WITH AUTHENTICATION SUPPORT

CLASS METHODS:
    InstagramScraper.login() -> AUTHENTICATES WITH INSTAGRAM
    InstagramScraper.scrape() -> DOWNLOADS POSTS FROM INSTAGRAM PROFILE
    main() -> PARSES ARGUMENTS AND RUNS SCRAPER
═══════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import argparse
import shutil
import time
from pathlib import Path
from typing import List, Dict, Optional
import instaloader  # type: ignore
import getpass


class InstagramScraper:

    def __init__(self, handle: str, max_posts: int = 3, 
                 username: Optional[str] = None, password: Optional[str] = None):
        self.handle = handle.replace('@', '').strip()
        self.max_posts = max_posts
        self.username = username or os.getenv('INSTAGRAM_USERNAME')
        self.password = password or os.getenv('INSTAGRAM_PASSWORD')
        
        project_root = Path(__file__).parent.parent.parent
        self.save_dir = project_root / 'frontend' / 'public' / 'clients' / self.handle / 'instagram'
        self.session_dir = project_root / 'backend' / '.instagram_sessions'
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        self.loader = instaloader.Instaloader(
            download_videos=True,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
            post_metadata_txt_pattern='',
            quiet=True,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            request_timeout=30.0,
            max_connection_attempts=3,
        )
    
    def login(self) -> bool:
        if not self.username or not self.password:
            print("\n⚠️  WARNING: No Instagram credentials provided!")
            print("   Instagram blocks unauthenticated scraping attempts.")
            print("\n   Set credentials via:")
            print("   1. Environment variables: INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD")
            print("   2. Command line: --username and --password")
            print("\n   Attempting to continue without authentication (likely to fail)...")
            return False
        
        session_file = self.session_dir / f"session_{self.username}"
        
        if session_file.exists():
            try:
                print(f"🔑 Loading saved session for @{self.username}...")
                self.loader.load_session_from_file(self.username, str(session_file))
                print("✅ Session loaded successfully")
                time.sleep(1)
                return True
            except Exception as e:
                print(f"⚠️  Failed to load session: {str(e)}")
                print("   Will attempt fresh login...")
        
        try:
            print(f"🔐 Logging in as @{self.username}...")
            self.loader.login(self.username, self.password)
            print("✅ Login successful")
            
            try:
                self.loader.save_session_to_file(str(session_file))
                print(f"💾 Session saved to {session_file.name}")
            except Exception as e:
                print(f"⚠️  Could not save session: {str(e)}")
            
            time.sleep(2)
            
            return True
            
        except instaloader.exceptions.BadCredentialsException:
            print("❌ Invalid username or password")
            return False
        except instaloader.exceptions.TwoFactorAuthRequiredException:
            print("❌ Two-factor authentication required")
            print("   Please disable 2FA temporarily or use an app-specific password")
            return False
        except instaloader.exceptions.ConnectionException as e:
            print(f"❌ Connection error during login: {str(e)}")
            return False
        except Exception as e:
            print(f"❌ Login failed: {str(e)}")
            return False
        
    def scrape(self) -> Dict[str, any]:
        print(f"\n🚀 Starting Instagram scraper for @{self.handle}")
        print(f"📂 Save directory: {self.save_dir}")
        
        login_success = self.login()
        if not login_success and self.username:
            return {
                'success': False,
                'handle': self.handle,
                'error': 'Authentication failed. Please check your credentials.'
            }
        
        try:
            temp_dir = Path(f'/tmp/instagram_scraper_{self.handle}')
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            original_dir = os.getcwd()
            os.chdir(temp_dir)
            
            print(f"📱 Fetching profile @{self.handle}...")
            
            try:
                profile = instaloader.Profile.from_username(self.loader.context, self.handle)
            except instaloader.exceptions.ProfileNotExistsException:
                raise Exception(f"Profile @{self.handle} not found")
            except instaloader.exceptions.PrivateProfileNotFollowedException:
                raise Exception(f"Profile @{self.handle} is private")
            except instaloader.exceptions.ConnectionException as e:
                error_str = str(e)
                if "429" in error_str or "rate" in error_str.lower():
                    raise Exception(f"Instagram rate limit detected. Please wait 30-60 minutes and try again with authentication.")
                elif "401" in error_str or "403" in error_str:
                    raise Exception(f"Instagram blocked the request. Make sure you're logged in with valid credentials. Wait 30-60 minutes before retrying.")
                raise Exception(f"Connection failed: {error_str}. Try logging in with Instagram credentials.")
            except Exception as e:
                raise Exception(f"Failed to fetch profile: {str(e)}")
            
            print(f"✅ Profile found: {profile.full_name or self.handle}")
            print(f"🔍 Extracting latest {self.max_posts} posts...")
            
            posts_downloaded = 0
            downloaded_files = []
            retry_count = 0
            max_retries = 3
            
            for post_num, post in enumerate(profile.get_posts(), start=1):
                if posts_downloaded >= self.max_posts:
                    break
                
                try:
                    print(f"  ⬇️  Downloading post {post_num}/{self.max_posts}...")
                    
                    if post_num > 1:
                        delay = 3 + (post_num * 0.5)
                        time.sleep(delay)
                    
                    try:
                        self.loader.download_post(post, target=self.handle)
                        retry_count = 0
                    except instaloader.exceptions.ConnectionException as e:
                        error_str = str(e)
                        if "429" in error_str or "rate" in error_str.lower() or "401" in error_str or "403" in error_str:
                            retry_count += 1
                            if retry_count >= max_retries:
                                print(f"  ⚠️  Instagram blocked the request. You may need to wait 30-60 minutes.")
                                break
                            wait_time = retry_count * 60
                            print(f"  ⏳ Rate limit/block detected. Waiting {wait_time} seconds...")
                            time.sleep(wait_time)
                            try:
                                self.loader.download_post(post, target=self.handle)
                                retry_count = 0
                            except:
                                print(f"  ⚠️  Retry failed. Skipping this post.")
                                continue
                        else:
                            raise
                    
                    post_files = list(temp_dir.glob(f'{self.handle}/*.jpg')) + \
                                list(temp_dir.glob(f'{self.handle}/*.mp4')) + \
                                list(temp_dir.glob(f'{self.handle}/*.png'))
                    
                    if post_files:
                        latest_file = max(post_files, key=lambda p: p.stat().st_mtime)
                        posts_downloaded += 1
                        
                        self.save_dir.mkdir(parents=True, exist_ok=True)
                        
                        extension = latest_file.suffix
                        new_filename = f"post-{posts_downloaded}{extension}"
                        dest_path = self.save_dir / new_filename
                        
                        shutil.move(str(latest_file), str(dest_path))
                        downloaded_files.append(new_filename)
                        
                        print(f"  ✅ Saved: {new_filename}")
                        
                        for f in temp_dir.glob(f'{self.handle}/*'):
                            try:
                                f.unlink()
                            except:
                                pass
                    
                except Exception as e:
                    print(f"  ⚠️  Failed to download post {post_num}: {str(e)[:100]}")
                    continue
            
            os.chdir(original_dir)
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
            
            if posts_downloaded == 0:
                raise Exception("No posts could be downloaded. Profile might have no posts or all downloads failed.")
            
            return {
                'success': True,
                'handle': self.handle,
                'posts_found': posts_downloaded,
                'posts_downloaded': posts_downloaded,
                'files': downloaded_files,
                'save_directory': str(self.save_dir)
            }
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            try:
                os.chdir(original_dir)
                shutil.rmtree(temp_dir)
            except:
                pass
            
            return {
                'success': False,
                'handle': self.handle,
                'error': str(e)
            }


def main():
    parser = argparse.ArgumentParser(
        description='Scrape latest posts from an Instagram profile using Instaloader',
        epilog='Note: Instagram authentication is required. Use --username/--password or set INSTAGRAM_USERNAME/INSTAGRAM_PASSWORD environment variables.'
    )
    parser.add_argument(
        'handle',
        help='Instagram handle (with or without @)'
    )
    parser.add_argument(
        '--max-posts',
        type=int,
        default=3,
        help='Maximum number of posts to scrape (default: 3)'
    )
    parser.add_argument(
        '--username',
        help='Instagram username for authentication'
    )
    parser.add_argument(
        '--password',
        help='Instagram password for authentication'
    )
    
    args = parser.parse_args()
    
    username = args.username
    password = args.password
    
    if username and not password:
        password = getpass.getpass("Enter Instagram password: ")
    
    scraper = InstagramScraper(args.handle, args.max_posts, username, password)
    result = scraper.scrape()
    
    print("\n" + "="*50)
    if result['success']:
        print("✅ SCRAPING COMPLETED SUCCESSFULLY")
        print(f"📊 Handle: @{result['handle']}")
        print(f"📸 Posts downloaded: {result['posts_downloaded']}")
        print(f"📂 Location: {result['save_directory']}")
        print(f"📄 Files: {', '.join(result['files'])}")
    else:
        print("❌ SCRAPING FAILED")
        print(f"📊 Handle: @{result['handle']}")
        print(f"⚠️  Error: {result['error']}")
    print("="*50)
    
    return 0 if result['success'] else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
