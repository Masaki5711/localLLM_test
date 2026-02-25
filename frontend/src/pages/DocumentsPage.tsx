import { useState, useCallback, type ChangeEvent } from 'react'
import { useAuthStore } from '../stores/auth'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api/v1'

interface UploadResult {
  document_id: string
  status: string
  chunk_count: number
  message: string
}

export function DocumentsPage() {
  const [uploading, setUploading] = useState(false)
  const [results, setResults] = useState<UploadResult[]>([])
  const [error, setError] = useState('')
  const accessToken = useAuthStore((s) => s.accessToken)

  const handleFileChange = useCallback(
    async (e: ChangeEvent<HTMLInputElement>) => {
      const files = e.target.files
      if (!files?.length) return

      setUploading(true)
      setError('')

      for (const file of Array.from(files)) {
        const formData = new FormData()
        formData.append('file', file)

        try {
          const res = await fetch(`${API_BASE}/documents/upload`, {
            method: 'POST',
            headers: {
              ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
            },
            body: formData,
          })

          if (!res.ok) {
            const err = await res.json().catch(() => ({}))
            throw new Error(err?.detail || `Upload failed: ${res.status}`)
          }

          const data = await res.json()
          setResults((prev) => [data.data, ...prev])
        } catch (err) {
          setError(err instanceof Error ? err.message : 'Upload failed')
        }
      }

      setUploading(false)
      e.target.value = ''
    },
    [accessToken],
  )

  return (
    <div className="flex h-screen flex-col bg-gray-50">
      <header className="border-b bg-white px-6 py-3">
        <h1 className="text-lg font-bold text-gray-900">ドキュメント管理</h1>
      </header>

      <main className="flex-1 overflow-y-auto p-6">
        <div className="mx-auto max-w-3xl">
          <div className="rounded-lg border-2 border-dashed border-gray-300 bg-white p-8 text-center">
            <p className="mb-4 text-gray-500">
              PDF または Word ファイルをアップロード
            </p>
            <label className="inline-block cursor-pointer rounded-lg bg-blue-600 px-6 py-2 text-white hover:bg-blue-700">
              {uploading ? '処理中...' : 'ファイルを選択'}
              <input
                type="file"
                accept=".pdf,.docx"
                multiple
                onChange={handleFileChange}
                className="hidden"
                disabled={uploading}
              />
            </label>
          </div>

          {error && (
            <div className="mt-4 rounded-md bg-red-50 p-3 text-sm text-red-700">
              {error}
            </div>
          )}

          {results.length > 0 && (
            <div className="mt-6">
              <h2 className="mb-3 text-sm font-medium text-gray-700">
                処理結果
              </h2>
              {results.map((r, i) => (
                <div
                  key={i}
                  className="mb-2 rounded-lg bg-white p-4 shadow-sm border border-gray-200"
                >
                  <p className="text-sm font-medium text-gray-900">
                    {r.message}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    チャンク数: {r.chunk_count} | ステータス: {r.status}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
