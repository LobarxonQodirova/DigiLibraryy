FROM node:18-alpine AS build

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci --silent

COPY . .
RUN npm run build

# Production stage: serve with a lightweight static server
FROM nginx:1.25-alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY --from=build /app/dist /app/build

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
