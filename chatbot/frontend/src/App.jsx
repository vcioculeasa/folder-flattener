import React, { useState } from 'react'

export default function App() {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState([])

  const sendMessage = async () => {
    if (!input) return
    const userMsg = { role: 'user', text: input }
    setMessages(m => [...m, userMsg])
    setInput('')
    const res = await fetch('http://localhost:8000/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: userMsg.text })
    })
    const data = await res.json()
    setMessages(m => [...m, { role: 'bot', text: data.reply }])
  }

  return (
    <div style={{ maxWidth: 600, margin: '0 auto', fontFamily: 'sans-serif' }}>
      <h2>Chatbot</h2>
      <div style={{ border: '1px solid #ccc', padding: 10, height: 300, overflowY: 'scroll' }}>
        {messages.map((m, i) => (
          <div key={i} style={{ textAlign: m.role === 'user' ? 'right' : 'left' }}>
            <span style={{ background: m.role === 'user' ? '#acf' : '#eee', padding: '4px 8px', borderRadius: 4, display: 'inline-block', margin: '4px 0' }}>
              {m.text}
            </span>
          </div>
        ))}
      </div>
      <div style={{ marginTop: 10 }}>
        <input
          style={{ width: '80%' }}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' ? sendMessage() : null}
        />
        <button onClick={sendMessage} style={{ width: '18%' }}>Send</button>
      </div>
    </div>
  )
}
