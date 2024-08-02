import useUploadedFiles from "../../hooks/useUploadedFiles";
import "./UploadedFiles.css";

import {
  ArrowPathIcon,
  ExclamationTriangleIcon,
} from "@heroicons/react/24/outline";
import UploadedFilesList from "./UploadedFilesList";
import { TooltipWrapper } from "../ui-components/tooltip/TooltipWrapper";
import { useUploadContext } from "../../hooks/useUploadContext";
import { useCallback, useEffect } from "react";

export default function UploadedFiles() {
  const {
    data: uploadedfiles,
    refetchList,
    onDateChange,
    listDate,
    error,
    isLoading,
  } = useUploadedFiles();
  const { isFileUploaded, setIsFileUploaded } = useUploadContext();

  useEffect(() => {
    if (isFileUploaded) {
      setIsFileUploaded(false);
      refetchList(new Date());
    }
  }, [isFileUploaded, setIsFileUploaded, refetchList]);

  const reloadListHandler = useCallback(() => {
    refetchList();
  }, [refetchList]);

  return (
    <div className="w-full py-10 px-10 lg:w-[1000px] bg-gray-100 rounded-lg  border-2 border-white/20 shadow-sm">
      <div className="flex items-center justify-between border-b border-gray-900/10 pb-5 mb-5">
        <h2 className="text-base font-semibold leading-4 text-lg text-gray-900">
          Uploaded files
        </h2>
        <div className="flex">
          <input
            type="date"
            value={listDate}
            onChange={onDateChange}
            className="block flex-1 border border-1 border-gray-900/10 bg-transparent rounded-md pl-1 text-gray-900 placeholder:text-gray-400 focus:ring-0 sm:text-sm sm:leading-6"
          />
          <button
            className="group relative w-8 h-8 border border-1 border-gray-900/10 p-1 rounded-md hover:rounded-full ml-2"
            title="Reload"
            onClick={reloadListHandler}
          >
            <ArrowPathIcon className="group-hover:animate-spin" />
            <TooltipWrapper>Reload</TooltipWrapper>
          </button>
        </div>
      </div>

      {error && !isLoading ? (
        <div className="text-red-700 text-center p-10">
          <ExclamationTriangleIcon className="w-6 h-6 inline-block" /> Something
          went wrong, try again later or contact support!
        </div>
      ) : (
        <UploadedFilesList
          uploadedfiles={uploadedfiles}
          selectedDate={listDate}
          isLoading={isLoading}
        />
      )}
    </div>
  );
}
