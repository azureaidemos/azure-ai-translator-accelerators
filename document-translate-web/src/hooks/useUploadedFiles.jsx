// src/hooks/useUploadedFiles.js
import { useState, useCallback, useEffect } from "react";
import axios from "axios";
import { GET_LOGS_API, API_KEY } from "../constants/apiConstants.js";
import { formatDate } from "../helpers/dateHelpers.js";

const useUploadedFiles = () => {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [listDate, setListDate] = useState(formatDate(new Date()));

  const onDateChange = useCallback(
    (date) => {
      setListDate(formatDate(date.target.valueAsDate));
    },
    [setListDate]
  );

  const getUploadedFiles = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await axios.get(GET_LOGS_API(listDate), {
        headers: {
          Accept: "application/json",
          "Ocp-Apim-Subscription-Key": API_KEY,
        },
      });
      setData(response.data);
    } catch (err) {
      setError(err);
    } finally {
      setIsLoading(false);
    }
  }, [setData, setError, setIsLoading, listDate]);

  const refetchList = useCallback(
    (date) => {
      if (!date || formatDate(date) === listDate) getUploadedFiles();
      else setListDate(formatDate(date));
    },
    [listDate, getUploadedFiles]
  );

  useEffect(() => {
    getUploadedFiles();
  }, [getUploadedFiles]);

  return {
    data,
    error,
    isLoading,
    setListDate,
    listDate,
    onDateChange,
    refetchList,
  };
};

export default useUploadedFiles;
