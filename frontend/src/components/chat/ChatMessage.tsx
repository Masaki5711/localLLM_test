import type { ChatMessage as ChatMessageType } from '../../hooks/useChat'

interface Props {
  message: ChatMessageType
}

export function ChatMessageComponent({ message }: Props) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-[80%] rounded-lg px-4 py-3 ${
          isUser
            ? 'bg-blue-600 text-white'
            : 'bg-white text-gray-900 shadow-sm border border-gray-200'
        }`}
      >
        <div className="whitespace-pre-wrap text-sm">{message.content}</div>
        {message.isStreaming && (
          <span className="inline-block animate-pulse text-gray-400">|</span>
        )}

        {message.sources && message.sources.length > 0 && (
          <div className="mt-3 border-t border-gray-200 pt-2">
            <p className="text-xs font-medium text-gray-500 mb-1">参照元:</p>
            {message.sources.map((src, i) => (
              <div
                key={i}
                className="mb-1 rounded bg-gray-50 p-2 text-xs text-gray-600"
              >
                <span className="font-medium">{src.file_name}</span>
                {src.heading && <span className="ml-1 text-gray-400">- {src.heading}</span>}
                <p className="mt-1 text-gray-500 line-clamp-2">{src.text}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
