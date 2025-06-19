#!/usr/bin/env python3
"""
JSON Generator and S3 Uploader
Creates 3000 unique JSON files (~50GB total) and uploads them to a new S3 bucket.
"""

import os
import json
import random
import string
import time
import boto3
import concurrent.futures
from datetime import datetime
from botocore.exceptions import ClientError, NoCredentialsError

class JSONS3Generator:
    def __init__(self):
        self.s3_client = None
        self.bucket_name = None
        self.output_dir = "generated_json"
        self.total_files = 3000
        self.target_total_size_gb = 4  # Changed from 50GB to 4GB
        self.max_workers = 10  # Number of parallel upload threads
        
    def setup_aws_credentials(self):
        """Setup AWS credentials and S3 client using CLI user role."""
        try:
            # Use default credentials from AWS CLI
            self.s3_client = boto3.client('s3')
            # Test credentials by listing buckets
            self.s3_client.list_buckets()
            print("✅ AWS credentials configured successfully (using CLI user role)")
            return True
        except NoCredentialsError:
            print("❌ AWS credentials not found!")
            print("Please ensure you are logged in to AWS CLI:")
            print("1. Run: aws configure")
            print("2. Or use: aws sso login (if using SSO)")
            print("3. Or ensure you have appropriate IAM role assigned")
            return False
        except ClientError as e:
            print(f"❌ AWS authentication error: {e}")
            return False
    
    def generate_bucket_name(self):
        """Generate a unique bucket name with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.bucket_name = f"cursor-json-bucket-{timestamp}"
        return self.bucket_name
    
    def create_s3_bucket(self):
        """Create a new S3 bucket."""
        try:
            print(f"🪣 Creating S3 bucket: {self.bucket_name}")
            self.s3_client.create_bucket(Bucket=self.bucket_name)
            print(f"✅ S3 bucket '{self.bucket_name}' created successfully")
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'BucketAlreadyExists':
                print(f"⚠️  Bucket '{self.bucket_name}' already exists, using existing bucket")
                return True
            else:
                print(f"❌ Error creating bucket: {e}")
                return False
    
    def generate_funny_filename(self):
        """Generate a funny and unique filename."""
        adjectives = [
            "fluffy", "sparkly", "bouncy", "silly", "wobbly", "giggly", "squishy",
            "twinkly", "bubbly", "fuzzy", "wacky", "zippy", "snuggly", "dizzy",
            "jumpy", "wiggly", "sparkly", "bouncy", "silly", "wobbly", "giggly"
        ]
        
        nouns = [
            "toaster", "penguin", "banana", "robot", "unicorn", "taco", "ninja",
            "dragon", "pizza", "wizard", "kitten", "rainbow", "spaghetti", "vampire",
            "turtle", "rocket", "butterfly", "sushi", "ghost", "mermaid", "taco"
        ]
        
        # Generate random components
        adj = random.choice(adjectives)
        noun = random.choice(nouns)
        number = random.randint(1, 999)
        suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        
        return f"{adj}-{noun}-{number}-{suffix}.json"
    
    def generate_random_json_content(self, target_size_bytes):
        """Generate random JSON content with target size - FIXED VERSION."""
        # Base structure
        data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "file_id": ''.join(random.choices(string.ascii_letters + string.digits, k=16)),
                "version": "1.0"
            },
            "data": {}
        }
        
        # Calculate target size per file (4GB / 3000 files ≈ 1.33MB per file)
        target_size_per_file = (self.target_total_size_gb * 1024 * 1024 * 1024) // self.total_files
        
        # Generate large chunks of data to reach target size efficiently
        chunk_size = 10000  # Generate 10KB chunks at a time
        keys_generated = 0
        
        while len(json.dumps(data)) < target_size_bytes:
            # Generate a chunk of data
            for chunk_idx in range(chunk_size):
                key = f"field_{keys_generated}_{''.join(random.choices(string.ascii_lowercase, k=8))}"
                
                # Generate larger data to reach target size faster
                data_type = random.choice(['string', 'number', 'array', 'object', 'boolean'])
                
                if data_type == 'string':
                    # Generate much larger strings
                    str_length = random.randint(100, 2000)
                    value = ''.join(random.choices(string.ascii_letters + string.digits + ' ', k=str_length))
                elif data_type == 'number':
                    value = random.uniform(-1000000, 1000000)
                elif data_type == 'array':
                    # Generate larger arrays
                    array_length = random.randint(50, 200)
                    value = [random.randint(1, 1000) for _ in range(array_length)]
                elif data_type == 'object':
                    # Generate larger objects
                    obj_length = random.randint(10, 50)
                    value = {f"nested_{i}": random.randint(1, 100) for i in range(obj_length)}
                else:  # boolean
                    value = random.choice([True, False])
                
                data["data"][key] = value
                keys_generated += 1
                
                # Check if we've reached target size
                if len(json.dumps(data)) >= target_size_bytes:
                    break
            
            # Safety check to prevent infinite loops
            if keys_generated > 100000:  # Max 100k keys per file
                break
        
        return data
    
    def create_output_directory(self):
        """Create the output directory for JSON files."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"📁 Created output directory: {self.output_dir}")
    
    def generate_json_files(self):
        """Generate all JSON files locally."""
        print(f"\n📝 Generating {self.total_files} JSON files...")
        
        # Calculate target size per file (4GB / 3000 files ≈ 1.33MB per file)
        target_size_per_file = (self.target_total_size_gb * 1024 * 1024 * 1024) // self.total_files
        
        total_generated_size = 0
        files_created = []
        
        for i in range(self.total_files):
            # Generate filename
            filename = self.generate_funny_filename()
            filepath = os.path.join(self.output_dir, filename)
            
            # Generate content with some size variation (±20%)
            size_variation = random.uniform(0.8, 1.2)
            target_size = int(target_size_per_file * size_variation)
            
            # Generate JSON content
            json_content = self.generate_random_json_content(target_size)
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(json_content, f, indent=2)
            
            # Get actual file size
            actual_size = os.path.getsize(filepath)
            total_generated_size += actual_size
            
            files_created.append({
                'filename': filename,
                'filepath': filepath,
                'size': actual_size
            })
            
            # Progress update every 100 files
            if (i + 1) % 100 == 0:
                progress = ((i + 1) / self.total_files) * 100
                size_mb = total_generated_size / (1024 * 1024)
                print(f"📊 Progress: {i + 1}/{self.total_files} ({progress:.1f}%) - {size_mb:.1f} MB generated")
        
        print(f"✅ Generated {len(files_created)} JSON files")
        print(f"📊 Total size: {total_generated_size / (1024 * 1024 * 1024):.2f} GB")
        
        return files_created
    
    def upload_single_file(self, file_info):
        """Upload a single file to S3 - used for parallel processing."""
        try:
            self.s3_client.upload_file(
                file_info['filepath'],
                self.bucket_name,
                file_info['filename']
            )
            return True, file_info['size']
        except ClientError as e:
            print(f"❌ Error uploading {file_info['filename']}: {e}")
            return False, 0
    
    def upload_to_s3(self, files_created):
        """Upload all generated files to S3 using parallel processing."""
        print(f"\n☁️  Uploading files to S3 bucket: {self.bucket_name}")
        print(f"🚀 Using {self.max_workers} parallel upload threads for speed")
        
        total_uploaded = 0
        total_upload_size = 0
        completed_files = 0
        
        # Use ThreadPoolExecutor for parallel uploads
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all upload tasks
            future_to_file = {executor.submit(self.upload_single_file, file_info): file_info 
                            for file_info in files_created}
            
            # Process completed uploads
            for future in concurrent.futures.as_completed(future_to_file):
                file_info = future_to_file[future]
                try:
                    success, file_size = future.result()
                    if success:
                        total_uploaded += 1
                        total_upload_size += file_size
                    
                    completed_files += 1
                    
                    # Progress update every 100 files
                    if completed_files % 100 == 0:
                        progress = (completed_files / len(files_created)) * 100
                        size_mb = total_upload_size / (1024 * 1024)
                        print(f"📤 Upload progress: {completed_files}/{len(files_created)} ({progress:.1f}%) - {size_mb:.1f} MB uploaded")
                
                except Exception as e:
                    print(f"❌ Exception uploading {file_info['filename']}: {e}")
                    completed_files += 1
        
        print(f"✅ Successfully uploaded {total_uploaded}/{len(files_created)} files to S3")
        print(f"📊 Total uploaded size: {total_upload_size / (1024 * 1024 * 1024):.2f} GB")
        
        return total_uploaded
    
    def cleanup_local_files(self):
        """Clean up local JSON files after upload."""
        try:
            import shutil
            shutil.rmtree(self.output_dir)
            print(f"🧹 Cleaned up local directory: {self.output_dir}")
        except Exception as e:
            print(f"⚠️  Could not clean up local files: {e}")
    
    def run(self):
        """Main execution method."""
        print("🚀 JSON Generator and S3 Uploader (Optimized)")
        print("=" * 50)
        
        # Setup AWS
        if not self.setup_aws_credentials():
            return False
        
        # Generate bucket name and create bucket
        self.generate_bucket_name()
        if not self.create_s3_bucket():
            return False
        
        # Create output directory
        self.create_output_directory()
        
        # Generate JSON files
        start_time = time.time()
        files_created = self.generate_json_files()
        
        # Upload to S3
        upload_start_time = time.time()
        uploaded_count = self.upload_to_s3(files_created)
        upload_end_time = time.time()
        
        # Calculate timing
        total_time = time.time() - start_time
        upload_time = upload_end_time - upload_start_time
        
        # Final summary
        print("\n" + "=" * 50)
        print("📋 FINAL SUMMARY")
        print("=" * 50)
        print(f"🪣 S3 Bucket: {self.bucket_name}")
        print(f"📁 Files generated: {len(files_created)}")
        print(f"📤 Files uploaded: {uploaded_count}")
        print(f"⏱️  Total time: {total_time:.2f} seconds")
        print(f"📤 Upload time: {upload_time:.2f} seconds")
        print(f"📊 Average upload speed: {len(files_created) / upload_time:.2f} files/second")
        print(f"🚀 Parallel uploads: {self.max_workers} threads")
        
        # Ask about cleanup
        cleanup = input("\n🧹 Clean up local JSON files? (y/n): ").lower().strip()
        if cleanup == 'y':
            self.cleanup_local_files()
        
        return True

def main():
    """Main function."""
    generator = JSONS3Generator()
    success = generator.run()
    
    if success:
        print("\n🎉 Process completed successfully!")
    else:
        print("\n❌ Process failed. Please check the error messages above.")

if __name__ == "__main__":
    main() 