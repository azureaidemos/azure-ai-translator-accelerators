import { useState, useCallback } from "react";
import axios from "axios";
import { UPLOAD_API, API_KEY } from "../constants/apiConstants.js";

const useUploadedFiles = () => {
  const [uploadResponse, setUploadResponse] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const uploadFile = useCallback(
    async (
      {
        fileToUpload,
        prompt_id,
        fromLang = "pn",
        toLang = "en",
        textToExclude = null,
      },
      successCallback,
      failCallback
    ) => {
      setIsLoading(true);
      setError(null);
      setUploadResponse(null);

      const formData = new FormData();
      formData.append(`file`, fileToUpload);
      formData.append(`prompt_id`, prompt_id);
      formData.append(`fromLang`, fromLang);
      formData.append(`toLang`, toLang);
      formData.append(`exclusion_text`, textToExclude || null);

      try {
        const response = await axios.post(UPLOAD_API, formData, {
          headers: {
            "Content-Type": "multipart/form-data",
            "Ocp-Apim-Subscription-Key": API_KEY,
          },
        });

        setUploadResponse(response);
        successCallback();
      } catch (err) {
        setError(err);
        failCallback(err);
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  return {
    uploadResponse,
    uploadError: error,
    uploadIsLoading: isLoading,
    uploadFile,
  };
};

export default useUploadedFiles;
