export function buildUpdateString(segments, value, action = "update") {
  const path = "[" + segments.map(String).join("][") + "]";
  const payload = JSON.stringify(value);
  return `${path}^${payload}^${action}`;
}
