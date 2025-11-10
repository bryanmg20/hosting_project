/**
 * API Utilities - Funciones helper
 */

/**
 * Normaliza una URL añadiendo el protocolo si no lo tiene
 * @param url - URL que puede o no tener protocolo
 * @returns URL normalizada con protocolo
 * 
 * @example
 * normalizeUrl('ccc.bryan.localhost') => 'http://ccc.bryan.localhost'
 * normalizeUrl('http://example.com') => 'http://example.com'
 * normalizeUrl('https://example.com') => 'https://example.com'
 */
export function normalizeUrl(url: string): string {
  if (!url) return url;
  
  // Si ya tiene protocolo, retornar tal cual
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url;
  }
  
  // Añadir http:// por defecto (localhost usa http)
  return `http://${url}`;
}
