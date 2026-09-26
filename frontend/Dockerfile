FROM node:20-alpine AS build
WORKDIR /srv/web
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

FROM node:20-alpine
WORKDIR /srv/web
COPY --from=build /srv/web/.next/standalone ./
COPY --from=build /srv/web/.next/static ./.next/static
COPY --from=build /srv/web/public ./public
EXPOSE 3000
CMD ["node", "server.js"]
