import { useEffect, useState } from 'react'
import './App.css'

interface News {
  title: string
}

function App() {
  const [news, setNews] = useState<News[] | null>(null)
  const [refresh, setRefresh] = useState<number>(0)
  const [isFetching, setIsFetching] = useState<boolean>(false)

  function fetchNews() {
    if (isFetching) return

    setIsFetching(true)

    fetch("https://api.chocolib.com/feed-entries", {
      headers: {
        'Content-Type': 'application/json'
      },
      // mode: 'no-cors'
    }).then(resp => {
      setIsFetching(false)
      console.log(resp)
      if (resp.ok) {
        resp.json().then(data => {
          setNews(data)
        })
      }
    })
  }

  useEffect(() => {
    fetchNews()
  }, [refresh])

  console.log(news)

  return (
    <>
      {news?.map(ele => <div key={Math.random()}>{ele.title}</div>)}
      <button onClick={() => setRefresh(Math.random())}>Refresh</button>
    </>
  )
}

export default App
