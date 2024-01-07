
FROM node:18-alpine


WORKDIR /app

COPY package*.json ./

RUN npm install --force

COPY frontend/package*.json ./frontend/

WORKDIR /app/frontend

RUN npm install --force

COPY ./frontend .

RUN npm run build

RUN npm install -g serve

EXPOSE 5000

CMD ["serve", "-s", "dist", "-l", "5000"]
