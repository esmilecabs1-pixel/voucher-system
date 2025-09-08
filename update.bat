@echo off
cd "C:\Users\BENJOR 2025-2026\Desktop\voucher"

echo === Staging all changes ===
git add .

echo === Committing changes ===
git commit -m "Auto update voucher system"

echo === Pulling latest from GitHub (with rebase) ===
git pull origin main --rebase

echo === Pushing to GitHub ===
git push origin main

echo === Done! Your changes are now on GitHub. ===
pause
