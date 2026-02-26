function transform(input) {
  const items = input.data;
  if (!items || !items.length) return { data: [] };

  const count = Math.min(30, items.length);
  const pool = [...items];
  for (let i = pool.length - 1; i > pool.length - count - 1; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [pool[i], pool[j]] = [pool[j], pool[i]];
  }

  const data = pool.slice(pool.length - count).map(raw => ({
    name: raw.name,
    image: raw.image,
    description: raw.description,
    rarity: raw.rarity && { name: raw.rarity.name, type: raw.rarity.type },
    collections: raw.collections?.map(c => ({ name: c.name })),
    wears: raw.wears?.map(w => ({ name: w.name })),
    pattern: raw.pattern && { name: raw.pattern.name },
    crates: raw.crates?.map(c => ({ name: c.name })),
    contains: raw.contains,
    exclusive_to: raw.exclusive_to,
  }));

  return { data };
}