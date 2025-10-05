import './ChatMessages.css'

function ChatMessages({ messages }) {
  const formatMessage = (text) => {
    return text.split('\n').map((paragraph, index) => (
      paragraph.trim() ? <p key={index}>{paragraph}</p> : <br key={index} />
    ))
  }

  return (
    <div className="messages">
      {messages.map(msg => (
        <div key={msg.id} className={`message ${msg.sender}`}>
          <div className={`message-content ${msg.isLoading ? 'loading' : ''}`}>
            {formatMessage(msg.text)}
          </div>
        </div>
      ))}
    </div>
  )
}

export default ChatMessages
