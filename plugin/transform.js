function transform(input) {
  const items = input.data;
  if (!items || !items.length) return { data: [] };

  const raw = items[Math.floor(Math.random() * items.length)];

  const item = {
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
  };

  return { data: [item] };
}