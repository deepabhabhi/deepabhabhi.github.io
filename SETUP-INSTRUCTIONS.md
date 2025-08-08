# GitHub Actions User Submission Setup

## ✅ What's Been Implemented

1. **Form validation** with mandatory name and email fields
2. **Data formatting**: Name in Title Case, Email in lowercase
3. **GitHub Actions integration** to save data to `users.txt`
4. **Error handling** with user-friendly messages

## 🔧 Configuration Required

### Step 1: Update Your Personal Access Token

1. In `index.html`, find line 294:
   ```javascript
   token: 'YOUR_PAT_TOKEN_HERE'  // Replace with your Personal Access Token
   ```

2. Replace `'YOUR_PAT_TOKEN_HERE'` with your actual PAT token:
   ```javascript
   token: 'ghp_your_actual_token_here'
   ```

### Step 2: Set Up GitHub Repository Secret

1. Go to your GitHub repository: `https://github.com/deepabhabhi/deepabhabhi.github.io`
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `PAT_TOKEN`
5. Value: Your Personal Access Token (same as above)
6. Click **Add secret**

### Step 3: PAT Token Permissions

Your Personal Access Token needs these permissions:
- ✅ **repo** (Full control of private repositories)
- ✅ **workflow** (Update GitHub Action workflows)

## 🚀 How It Works

1. User fills form and clicks Submit
2. JavaScript validates and formats the data
3. API call triggers GitHub Actions via repository dispatch
4. GitHub Actions workflow appends data to `users.txt`
5. Changes are automatically committed and pushed

## 📝 Data Format

Users will be saved in `users.txt` as:
```
Aman Gupta, abc@gmail.com
John Doe, john.doe@example.com
Jane Smith, jane.smith@gmail.com
```

## 🔍 Testing

1. Test with sample data: "aman gupta" and "ABC@GMAIL.COM"
2. Expected result: "Aman Gupta, abc@gmail.com"
3. Check GitHub Actions tab for workflow execution
4. Verify `users.txt` is updated automatically

## 🛠 Troubleshooting

- **403 Error**: Check PAT token permissions
- **404 Error**: Verify repository name and owner
- **Workflow not triggering**: Check repository secrets setup
- **Data not appearing**: Check GitHub Actions logs for errors

## 📁 Files Created/Modified

- ✅ `index.html` - Updated with form validation and GitHub API integration
- ✅ `.github/workflows/user-submission.yml` - GitHub Actions workflow
- ✅ `users.txt` - Will store user submissions
- ✅ `SETUP-INSTRUCTIONS.md` - This setup guide

## 🔒 Security Note

Never commit your PAT token directly to the repository. Always use GitHub Secrets for sensitive tokens.