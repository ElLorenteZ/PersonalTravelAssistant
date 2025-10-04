import './ChatMessages.css'

function ChatMessages({ messages }) {
  return (
    <div className="messages">
      {messages.map(msg => (
        <div key={msg.id} className={`message ${msg.sender}`}>
          <div className={`message-content ${msg.isLoading ? 'loading' : ''}`}>
            {msg.text}
          </div>
        </div>
      ))}
    </div>
  )
}

export default ChatMessages
