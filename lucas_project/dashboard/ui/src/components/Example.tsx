import React, { useEffect, useState } from 'react'

interface Kpis {
  domains: number
  revenue: number
}

export default function Example() {
  const [kpis, setKpis] = useState<Kpis | null>(null)
  const [finance, setFinance] = useState<{ profit: number } | null>(null)
  const [domains, setDomains] = useState<string[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchData() {
      try {
        const [kpisRes, financeRes, domainsRes] = await Promise.all([
          fetch('/api/kpis'),
          fetch('/api/finance'),
          fetch('/api/domains'),
        ])

        if (!kpisRes.ok || !financeRes.ok || !domainsRes.ok) {
          throw new Error('API request failed')
        }

        const kpisData = await kpisRes.json()
        const financeData = await financeRes.json()
        const domainsData = await domainsRes.json()

        setKpis(kpisData)
        setFinance(financeData)
        setDomains(domainsData)
      } catch (err) {
        setError((err as Error).message)
      }
    }

    fetchData()
  }, [])

  if (error) {
    return <div className="p-2 border rounded text-red-500">Error: {error}</div>
  }

  if (!kpis || !finance || !domains) {
    return <div className="p-2 border rounded">Loading...</div>
  }

  return (
    <div className="p-2 border rounded space-y-2">
      <div>
        KPIs: domains={kpis.domains}, revenue={kpis.revenue}
      </div>
      <div>Finance Profit: {finance.profit}</div>
      <div>
        Domains:
        <ul className="list-disc list-inside">
          {domains.map((d) => (
            <li key={d}>{d}</li>
          ))}
        </ul>
      </div>
    </div>
  )
}
