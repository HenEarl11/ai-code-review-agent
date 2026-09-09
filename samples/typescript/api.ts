const API_TOKEN = 'hardcoded-client-token';

export async function getData(url: string, options: any) {
  const response = await fetch(url, {
    ...options,
    headers: {
      Authorization: 'Bearer ' + API_TOKEN,
    },
  });

  return response.json();
}

export function parseUnsafe(input: string) {
  return eval(input);
}
