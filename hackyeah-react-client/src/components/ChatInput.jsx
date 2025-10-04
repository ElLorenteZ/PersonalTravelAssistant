import { useState } from 'react'
import './ChatInput.css'

function ChatInput({ onSend, isLoading }) {
  const [input, setInput] = useState('')

  const handleSend = () => {
    if (input.trim() && !isLoading) {
      onSend(input)
      setInput('')
    }
  }

  return (
    <div className="input-container">
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyPress={(e) => e.key === 'Enter' && handleSend()}
        placeholder="Type your message..."
        className="message-input"
        disabled={isLoading}
      />
      <button onClick={handleSend} className="send-btn" disabled={isLoading}>
        Send
      </button>
    </div>
  )
}

export default ChatInput
