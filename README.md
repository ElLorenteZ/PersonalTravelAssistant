1. Provide proper API keys in environment:
```{bash}
OPENAI_API_KEY=*
OPENWEATHER_API_KEY=*
```
2. Start docker compose.
```{bash}
docker-compose up
```

3. Create venv.
```{bash}
python3 -m venv hackyeah-env 
```

4. Switch to env.
```{bash}
source hackyeah-env/bin/activate
```

5. Install requirements.
```{bash}
pip3 install -r requirements.txt
```

6. Start backend app. Go to /hackyeah-chatcontroller. Start the app:
```{bash}
python3 app.py
```

7. Start frontend app. Go to /hackyeah-react-client. Start the app:
```{bash}
npm run dev
```