import { useRef, useEffect } from 'react'
import { useChat } from '../hooks/useChat'
import { ChatMessageComponent } from '../components/chat/ChatMessage'
import { ChatInput } from '../components/chat/ChatInput'
import { useAuthStore } from '../stores/auth'

export function ChatPage() {
  const { messages, isLoading, sendMessage, clearMessages } = useChat()
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const user = useAuthStore((s) => s.user)
  const logout = useAuthStore((s) => s.logout)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  return (
    <div className="flex h-screen flex-col bg-gray-50">
      <header className="flex items-center justify-between border-b bg-white px-6 py-3">
        <div>
          <h1 className="text-lg font-bold text-gray-900">
            Factory Knowledge GraphRAG
          </h1>
          <p className="text-xs text-gray-500">生産工場ナレッジ検索システム</p>
        </div>
        <div className="flex items-center gap-4">
          {messages.length > 0 && (
            <button
              onClick={clearMessages}
              className="text-sm text-gray-500 hover:text-gray-700"
            >
              新しい会話
            </button>
          )}
          <span className="text-sm text-gray-600">
            {user?.display_name || user?.username}
          </span>
          <button
            onClick={logout}
            className="rounded border border-gray-300 px-3 py-1 text-sm text-gray-600 hover:bg-gray-100"
          >
            ログアウト
          </button>
        </div>
      </header>

      <main className="flex-1 overflow-y-auto p-6">
        <div className="mx-auto max-w-3xl">
          {messages.length === 0 ? (
            <div className="mt-20 text-center">
              <h2 className="text-xl font-medium text-gray-400">
                何でも聞いてください
              </h2>
              <p className="mt-2 text-sm text-gray-400">
                工場のドキュメントに基づいて回答します
              </p>
              <div className="mt-8 flex flex-wrap justify-center gap-2">
                {[
                  'Aラインのチョコ停の原因は？',
                  'リフロー炉の温度プロファイル基準',
                  'はんだブリッジの対策方法',
                ].map((q) => (
                  <button
                    key={q}
                    onClick={() => sendMessage(q)}
                    className="rounded-full border border-gray-300 px-4 py-2 text-sm text-gray-600 hover:bg-white hover:shadow-sm"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((msg) => (
              <ChatMessageComponent key={msg.id} message={msg} />
            ))
          )}
          <div ref={messagesEndRef} />
        </div>
      </main>

      <footer className="border-t bg-white p-4">
        <div className="mx-auto max-w-3xl">
          <ChatInput onSend={sendMessage} disabled={isLoading} />
        </div>
      </footer>
    </div>
  )
}
