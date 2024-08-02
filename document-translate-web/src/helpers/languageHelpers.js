import { languageOptions } from "../constants/languageConstants";

export const getLanguageByCode = (code) => {
  return languageOptions.find((lang) => lang.value === code).label;
};
