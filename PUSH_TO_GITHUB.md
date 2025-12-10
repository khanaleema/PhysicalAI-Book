 # 🚀 GitHub Push aur Deploy Steps

## Step 1: GitHub Repository Create Karein

1. https://github.com/new par jao
2. Repository name: `PhysicalAI-Book` (ya kuch aur)
3. Public select karein
4. "Create repository" click karein

## Step 2: Code Push Karein

```bash
cd C:\Users\user\Desktop\PhysicalAI-Book

# Remote add karein (YOUR_USERNAME replace karein)
git remote add origin https://github.com/YOUR_USERNAME/PhysicalAI-Book.git

# Push karein
git push -u origin main
```

## Step 3: GitHub Pages Setup

1. Repository Settings → Pages
2. Source: "GitHub Actions" select karein
3. Save

## Step 4: Secret Add Karein (Optional)

1. Repository Settings → Secrets and variables → Actions
2. New repository secret:
   - Name: `API_URL`
   - Value: `https://aleemakhan-physical-ai-backend.hf.space`
3. Add secret

## ✅ Done!

Push ke baad automatically deploy hoga via GitHub Actions!

