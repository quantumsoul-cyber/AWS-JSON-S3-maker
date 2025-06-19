# JSON Generator and S3 Uploader

A Python application that generates 3000 unique JSON files (~50GB total) and uploads them to a new AWS S3 bucket. Perfect for testing AWS services, S3 performance simulations, and storage cost modeling.

## 🚀 Features

- **Unique S3 Bucket Creation**: Creates timestamped buckets (e.g., `cursor-json-bucket-20250619-143000`)
- **Massive JSON Generation**: Creates 3000 unique JSON files with randomized content
- **Funny Filenames**: Generates amusing, unique filenames like `fluffy-toaster-42-ab1x9z.json`
- **Size Control**: Targets ~50GB total across all files with size variation
- **Progress Tracking**: Real-time progress updates during generation and upload
- **AWS Integration**: Seamless S3 upload with proper error handling
- **Cleanup Options**: Optional local file cleanup after upload

## 📦 Technologies Used

- **Python 3.8+**
- **boto3** (AWS SDK for Python)
- **Standard Libraries**: `os`, `json`, `random`, `string`, `datetime`, `time`

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd aws-json-s3-maker
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure AWS CLI** (choose one method):
   
   **Option A: AWS CLI Configure**
   ```bash
   aws configure
   ```
   
   **Option B: AWS SSO (if using Single Sign-On)**
   ```bash
   aws sso login
   ```
   
   **Option C: IAM Role** (if running on EC2 or with assumed role)
   
   The application will automatically use your current AWS CLI session and role permissions.

## 🎯 Usage

1. **Ensure you're logged into AWS CLI**:
   ```bash
   aws sts get-caller-identity
   ```

2. **Run the application**:
   ```bash
   python json_s3_generator.py
   ```

The application will:
1. ✅ Verify AWS CLI credentials and permissions
2. 🪣 Create a new S3 bucket with timestamp
3. 📝 Generate 3000 JSON files locally
4. ☁️ Upload all files to S3
5. 📊 Display performance metrics
6. 🧹 Optionally clean up local files

## 📊 Output Example

```
🚀 JSON Generator and S3 Uploader
==================================================
✅ AWS credentials configured successfully
🪣 Creating S3 bucket: cursor-json-bucket-20250619-143000
✅ S3 bucket 'cursor-json-bucket-20250619-143000' created successfully
📁 Created output directory: generated_json

📝 Generating 3000 JSON files...
📊 Progress: 100/3000 (3.3%) - 1.7 GB generated
📊 Progress: 200/3000 (6.7%) - 3.4 GB generated
...
✅ Generated 3000 JSON files
📊 Total size: 50.12 GB

☁️  Uploading files to S3 bucket: cursor-json-bucket-20250619-143000
📤 Upload progress: 100/3000 (3.3%) - 1.7 GB uploaded
📤 Upload progress: 200/3000 (6.7%) - 3.4 GB uploaded
...
✅ Successfully uploaded 3000/3000 files to S3
📊 Total uploaded size: 50.12 GB

==================================================
📋 FINAL SUMMARY
==================================================
🪣 S3 Bucket: cursor-json-bucket-20250619-143000
📁 Files generated: 3000
📤 Files uploaded: 3000
⏱️  Total time: 1245.67 seconds
📤 Upload time: 892.34 seconds
📊 Average upload speed: 3.36 files/second

🧹 Clean up local JSON files? (y/n): y
🧹 Cleaned up local directory: generated_json

🎉 Process completed successfully!
```

## 🧪 Ideal Use Cases

- **AWS Service Testing**: Test S3 performance with large object sets
- **Load Simulations**: Simulate high-volume S3 operations
- **Cost Modeling**: Estimate storage and API costs for large datasets
- **Performance Benchmarking**: Measure upload speeds and throughput
- **Development Testing**: Create realistic test data for applications

## ⚙️ Configuration

You can modify the following parameters in `json_s3_generator.py`:

```python
class JSONS3Generator:
    def __init__(self):
        self.total_files = 3000          # Number of files to generate
        self.target_total_size_gb = 50   # Target total size in GB
        self.output_dir = "generated_json"  # Local output directory
```

## 🔧 Customization

### Modify File Content
Edit the `generate_random_json_content()` method to customize JSON structure:

```python
def generate_random_json_content(self, target_size_bytes):
    # Customize the base structure
    data = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "file_id": ''.join(random.choices(string.ascii_letters + string.digits, k=16)),
            "version": "1.0",
            "custom_field": "your_value"
        },
        "data": {}
    }
    # ... rest of the method
```

### Add More Funny Names
Extend the `generate_funny_filename()` method with more adjectives and nouns:

```python
adjectives = [
    "fluffy", "sparkly", "bouncy", "silly", "wobbly", "giggly", "squishy",
    "twinkly", "bubbly", "fuzzy", "wacky", "zippy", "snuggly", "dizzy",
    "jumpy", "wiggly", "your_new_adjective"
]
```

## 🚨 Important Notes

- **AWS CLI Required**: Ensure you're logged into AWS CLI with appropriate S3 permissions
- **Storage Requirements**: Ensure you have at least 50GB of free disk space
- **Network Bandwidth**: Uploading 50GB requires good internet connection
- **AWS Costs**: S3 storage and API calls will incur charges based on your account
- **Time**: The process may take 15-30 minutes depending on your setup
- **Permissions**: Your AWS CLI user/role needs S3 bucket creation and upload permissions

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

If you encounter any issues or have questions, please open an issue on GitHub.

---

**Happy JSON generating! 🎉** 