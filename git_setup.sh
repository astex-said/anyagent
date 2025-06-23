#!/bin/bash

# После создания GitHub репозитория выполните эти команды:

echo "🔗 Setting up git remote..."

# Добавляем remote (замените YOUR_USERNAME на ваш GitHub username)
git remote add origin https://github.com/astex-said/anyagent.git

# Устанавливаем upstream branch
git branch -M main

# Пушим код
git push -u origin main

echo "✅ Repository pushed to GitHub!"
echo "🔗 Visit: https://github.com/astex-said/anyagent"