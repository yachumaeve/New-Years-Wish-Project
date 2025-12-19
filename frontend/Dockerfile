# 階段 1: Build
FROM node:22 AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build --configuration=production

# 階段 2: Run
FROM nginx:stable-alpine
# 將 Angular 編譯出的 dist 資料夾內容複製到 Nginx
COPY --from=build /app/dist/frontend/browser /usr/share/nginx/html
# 複製自定義的 Nginx 設定
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80