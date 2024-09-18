FROM node:21.7.1-alpine
WORKDIR /app
COPY package*.json ./
RUN npm config set registry https://registry.npmmirror.com
RUN npm install --legacy-peer-deps 
COPY . ./
RUN npm run build
CMD cp -r build result_build