// Dependency-free validation for the JSON Schema keywords used by this study.
// Unsupported keywords fail closed, so extending a contract cannot silently
// weaken the online gate or offline checks. No backend or agent is imported.
import { isDeepStrictEqual } from 'node:util';

const supported = new Set(['type', 'properties', 'required', 'additionalProperties', 'items', 'enum', 'minimum', 'minLength', 'uniqueItems', 'description']);
export function schemaErrors(schema, value, path = '$') {
  for (const key of Object.keys(schema)) if (!supported.has(key)) throw new Error(`Unsupported schema keyword: ${key}`);
  const errors = [];
  const object = value !== null && typeof value === 'object' && !Array.isArray(value);
  const validType = {
    object, array: Array.isArray(value), string: typeof value === 'string',
    boolean: typeof value === 'boolean', integer: Number.isInteger(value),
    number: typeof value === 'number' && Number.isFinite(value), null: value === null,
  }[schema.type];
  if (!validType) return [`${path}: expected ${schema.type}`];
  if (schema.enum && !schema.enum.some(item => isDeepStrictEqual(item, value))) errors.push(`${path}: value is outside enum`);
  if (schema.minimum !== undefined && value < schema.minimum) errors.push(`${path}: below minimum`);
  if (schema.minLength !== undefined && value.length < schema.minLength) errors.push(`${path}: string is too short`);
  if (schema.type === 'object') {
    for (const key of schema.required ?? []) if (!Object.hasOwn(value, key)) errors.push(`${path}.${key}: required`);
    for (const [key, item] of Object.entries(value)) {
      if (Object.hasOwn(schema.properties ?? {}, key)) errors.push(...schemaErrors(schema.properties[key], item, `${path}.${key}`));
      else if (schema.additionalProperties === false) errors.push(`${path}.${key}: additional property`);
    }
  }
  if (schema.type === 'array') {
    for (const [index, item] of value.entries()) errors.push(...schemaErrors(schema.items, item, `${path}[${index}]`));
    if (schema.uniqueItems && value.some((item, index) => value.slice(0, index).some(other => isDeepStrictEqual(item, other)))) errors.push(`${path}: duplicated array item`);
  }
  return errors;
}
