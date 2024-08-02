import { useState, useCallback, useEffect } from "react";
import axios from "axios";
import { GET_PROMPTS_API, API_KEY } from "../constants/apiConstants.js";

const useGetPrompts = () => {
  const [promptsList, setPromptsList] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const getUploadedFiles = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await axios.get(GET_PROMPTS_API, {
        headers: {
          Accept: "application/json",
          "Ocp-Apim-Subscription-Key": API_KEY,
        },
      });
      setPromptsList(response?.data?.map(prompt => ({
        ...prompt,
        prompt_text: prompt.prompt_text?.replace(/\\n/g , "<br>")
      })));
    } catch (err) {
      setError(err);
    } finally {
      setIsLoading(false);
    }
  }, [setPromptsList, setError, setIsLoading]);

  useEffect(() => {
    getUploadedFiles();
  }, [getUploadedFiles]);

  return {
    promptsList,
    error,
    isLoading,
  };
};

export default useGetPrompts;
