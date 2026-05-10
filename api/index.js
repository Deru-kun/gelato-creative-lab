const express = require('express');
const { Client } = require('pg');
const cors = require('cors');
if (process.env.NODE_ENV !== 'production') {
  require('dotenv').config({ path: '../.env' });
}

const app = express();
const port = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

const client = new Client({
  connectionString: process.env.DB_URL,
  ssl: {
    rejectUnauthorized: false
  }
});

client.connect();

// Basic search endpoint
app.get(['/api/search', '/search'], async (req, res) => {
  const { q } = req.query;
  if (!q) return res.json([]);

  try {
    // Search in products by name or flavor
    // We use technical categories to filter
    const query = `
      SELECT p.*, m.name as manufacturer_name, tc.name as technical_category_name
      FROM products p
      JOIN manufacturers m ON p.manufacturer_id = m.id
      JOIN technical_categories tc ON p.technical_category_id = tc.id
      WHERE p.name ILIKE $1 OR p.description ILIKE $1
      LIMIT 10
    `;
    const result = await client.query(query, [`%${q}%`]);
    res.json(result.rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Advanced concept matching
app.post(['/api/match-concept', '/match-concept'], async (req, res) => {
  const { concept } = req.body;
  // This would ideally use an LLM, but we'll use a keyword-based matcher for now
  const keywords = concept.toLowerCase().split(/[ ,]+/).filter(w => w.length > 2);
  
  try {
    const results = {
      paste: [],
      variegature: [],
      inclusioni: []
    };

    for (const word of keywords) {
      const query = `
        SELECT p.*, m.name as manufacturer_name, tc.slug as category_slug
        FROM products p
        JOIN manufacturers m ON p.manufacturer_id = m.id
        JOIN technical_categories tc ON p.technical_category_id = tc.id
        WHERE (p.name ILIKE $1 OR p.description ILIKE $1)
        LIMIT 3
      `;
      const resMatch = await client.query(query, [`%${word}%`]);
      
      for (const row of resMatch.rows) {
        if (row.category_slug === 'paste') results.paste.push(row);
        if (row.category_slug === 'variegate') results.variegature.push(row);
        if (row.category_slug === 'inclusion') results.inclusioni.push(row);
      }
    }

    // Deduplicate and limit
    res.json({
      paste: [...new Map(results.paste.map(item => [item.id, item])).values()].slice(0, 5),
      variegature: [...new Map(results.variegature.map(item => [item.id, item])).values()].slice(0, 5),
      inclusioni: [...new Map(results.inclusioni.map(item => [item.id, item])).values()].slice(0, 5)
    });

  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

if (require.main === module) {
  app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
  });
}

module.exports = app;
