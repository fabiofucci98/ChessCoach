FROM node:22

WORKDIR /app

# Copia i file dei requisiti
COPY package*.json ./

# Pulisce eventuali cache di npm e installa tutte le dipendenze (incluse quelle opzionali per musl)
RUN npm ci || npm install

# Copia il codice sorgente
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]