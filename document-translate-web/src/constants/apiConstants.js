export const API_KEY = "API_KEY"; // Replace with your API key
export const BASE_URL =
  "https://apim-name.azure-api.net/translation-service-function"; // Replace with your API Management URL
export const GET_LOGS_API = (date) =>
  `${BASE_URL}/get_logs_by_date?date=${date}`;
export const GET_ALL_LOGS = `${BASE_URL}/get_all_logs`;
export const UPLOAD_API = `${BASE_URL}/upload_file`;
export const GET_PROMPTS_API = `${BASE_URL}/get_all_prompts`;