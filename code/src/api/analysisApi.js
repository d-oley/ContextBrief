const ML_URL = process.env.VUE_APP_ML_API_BASE_URL || ''

async function mlRequest(url, opts = {}) {
  const res = await fetch(url, {
    ...opts,
    headers: {
      'Content-Type': 'application/json',
      ...(opts.headers || {}),
    },
  })

  let data = null
  try {
    data = await res.json()
  } catch {
    if (!res.ok) throw new Error('Server error')
    return null
  }

  if (!res.ok) {
    const err = new Error(data?.message || 'ML service error')
    err.status = res.status
    err.body = data
    throw err
  }

  return data
}

export const analyzeTopic = ({ text }) =>
  mlRequest(`${ML_URL}/evaluate`, {
    method: 'POST',
    body: JSON.stringify({ text }),
  })
