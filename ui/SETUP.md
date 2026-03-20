# JARVIS UI - Complete Setup

## ✅ **HTML VERSION - READY NOW** 

**Status**: Running on port 3000

### Access it:
```
http://127.0.0.1:3000/index.html
```

### Features:
- ✅ Single file (no build step needed)
- ✅ Vanilla JavaScript
- ✅ Zero dependencies
- ✅ Chat with streaming
- ✅ Memory search
- ✅ Health status
- ✅ Permission modal
- ✅ Mobile responsive

### To run locally:
```bash
cd c:\D-Drive\Development\Jarvis\ui
python -m http.server 3000
# Then open: http://127.0.0.1:3000/index.html
```

---

## Next.js VERSION - TO SETUP

### Install and run:
```bash
cd c:\D-Drive\Development\Jarvis\ui\nextjs
npm install
npm run dev
```

Server will start on `http://127.0.0.1:3001`

### Or for production:
```bash
npm run build
npm start
```

---

## Troubleshooting

###HTML shows "Connection refused"?
- Make sure backend JARVIS is running on http://127.0.0.1:8888
- Check: `python test_api.py` in the main jarvis folder

### Can't send messages?
1. Check if Ollama is running: `ollama serve`
2. Pull the model: `ollama pull phi3-mini`
3. Verify health: Health indicator should show green dots

### Memory search empty?
- Send a message first, then search
- Memory learns from conversations over time

---

## API Endpoints Used

- `GET http://127.0.0.1:8888/health` - Service status
- `POST http://127.0.0.1:8888/chat` - Send message (streaming)
- `GET http://127.0.0.1:8888/tasks` - Chat history
- `GET http://127.0.0.1:8888/memory/search` - Memory search

---

## Performance Notes

- Search is debounced 500ms to reduce API calls
- Health check polls every 10 seconds
- CSS-only animations for low-end machines
- No heavy libraries like Framer Motion

---

## Browser Support

- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support  
- Mobile browsers: ✅ Responsive design

**Recommended**: Chrome or Edge for best performance