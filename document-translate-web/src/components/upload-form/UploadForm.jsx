import React, { useEffect } from "react";
import { XMarkIcon } from "@heroicons/react/24/solid";
import { useState, useCallback } from "react";
import Select from "react-select";
import useUploadForm from "../../hooks/useUploadForm";
import useNotifications from "../../hooks/useNotification";
import { DocumentArrowUpIcon } from "@heroicons/react/24/outline";
import "./UploadForm.css";
import { useDragDrop } from "../../hooks/useDragDrop";
import { useUploadContext } from "../../hooks/useUploadContext";
import { languageOptions } from "../../constants/languageConstants";
import useGetPrompts from "../../hooks/useGetPrompts";

export default function UploadForm() {
  const [fileToUpload, setFileToUpload] = useState(null);
  const [fromLang, setFromLang] = useState({ value: "pl", label: "Polish" });
  const [toLang, setToLang] = useState({ value: "en", label: "English" });
  const [prompt, setPrompt] = useState();
  const [exclusionTextBoxValue, setExclusionTextBoxValue] = useState(""); // State for multi-line text box
  const { uploadIsLoading, uploadFile } = useUploadForm();
  const { promptsList, isLoading: isPromptsLoading } = useGetPrompts();
  const { notifications, addNotification } = useNotifications();
  const {
    wrapperRef,
    onDragEnter,
    onDragLeave,
    onDrop,
    handleRemoveFile,
    handleFileChange,
  } = useDragDrop({ setFileToUpload });
  const { setIsFileUploaded } = useUploadContext();

  const onFormSubmit = useCallback(
    (event) => {
      event.preventDefault();

      uploadFile(
        {
          fileToUpload,
          fromLang: fromLang.value,
          toLang: toLang.value,
          textToExclude: exclusionTextBoxValue.trim() || null,
          prompt_id: prompt.id,
        },
        () => {
          addNotification(
            "success",
            <>
              File {fileToUpload.name} uploaded successfully! <br />
              Processing, translating and watermarking the file are in progress
              right now :)
            </>
          );
          setIsFileUploaded(true);
          setFileToUpload(null);
          setExclusionTextBoxValue("");
        },
        (error) => {
          addNotification(
            "error",
            error
              ? `Error uploading file: ${fileToUpload.name}. ${error.message}`
              : `Error uploading file: ${fileToUpload.name}`
          );
        }
      );
    },
    [
      uploadFile,
      prompt,
      fileToUpload,
      fromLang.value,
      toLang.value,
      exclusionTextBoxValue,
      addNotification,
      setIsFileUploaded,
    ]
  );

  useEffect(() => {
    if (!!promptsList?.length) setPrompt(promptsList[0]);
  }, [promptsList]);

  const getOptionLabel = useCallback((item) => item?.prompt_name, []);
  const getOptionValue = useCallback((item) => item?.id, []);

  return (
    <>
      {notifications.map(({ NotificationComponent, id, ...props }, index) => (
        <NotificationComponent key={id} index={index} {...props} />
      ))}
      <div className="w-full py-10 px-10 bg-gray-100 rounded-lg border-2 border-white/20 shadow-sm">
        <form onSubmit={onFormSubmit}>
          <div className="col-span-full">
            <label
              htmlFor="file-upload"
              className="block text-sm font-medium leading-6 text-gray-900"
            >
              File Upload
            </label>
            <div
              ref={wrapperRef}
              className="mt-2 flex justify-center rounded-lg border border-dashed border-gray-900/25 px-6 py-10"
              onDragEnter={onDragEnter}
              onDragOver={onDragEnter}
              onDragLeave={onDragLeave}
              onDrop={onDrop}
            >
              <div className="text-center w-full">
                {!!fileToUpload ? (
                  <div className="flex w-full text-center justify-between items-center">
                    <span>{fileToUpload?.name}</span>
                    <XMarkIcon
                      className="block w-5 h-5 p-1 cursor-pointer rounded-xl hover:bg-gray-500/50 hover:text-white"
                      alt="Cancel file upload"
                      onClick={handleRemoveFile}
                    />
                  </div>
                ) : (
                  <>
                    <DocumentArrowUpIcon
                      className="mx-auto h-12 w-12 text-gray-300"
                      aria-hidden="true"
                    />
                    <div className="mt-4 flex itemx-center justify-center text-sm leading-6 text-gray-600">
                      <label
                        htmlFor="file-upload"
                        className="relative cursor-pointer text-center"
                      >
                        <span className="font-bold">Upload a file</span>
                      </label>
                      <p className="pl-1">or drag and drop</p>
                    </div>
                    <p className="text-xs leading-5 text-gray-600">
                      DOCX, PDF up to 20MB
                    </p>
                    <input
                      id="file-upload"
                      name="file-upload"
                      type="file"
                      className="sr-only"
                      onChange={handleFileChange}
                      accept=".txt,.pdf,.docx,.doc"
                    />
                  </>
                )}
              </div>
            </div>
          </div>
          <div className="flex flex-wrap gap-x-5">
            <div className="mt-5 w-full sm:w-auto sm:flex-1">
              <label
                htmlFor="from-lang"
                className="block text-sm font-medium leading-6 text-gray-900"
              >
                From Language
              </label>
              <Select
                id="from-lang"
                name="from-lang"
                options={languageOptions}
                value={fromLang}
                onChange={setFromLang}
                className="mt-1"
              />
            </div>

            <div className="mt-5 w-full sm:w-auto sm:flex-1">
              <label
                htmlFor="to-lang"
                className="block text-sm font-medium leading-6 text-gray-900"
              >
                To Language
              </label>
              <Select
                id="to-lang"
                name="to-lang"
                options={languageOptions}
                value={toLang}
                onChange={setToLang}
                className="mt-1"
              />
            </div>

            <div className="mt-5 w-full">
              <label
                htmlFor="multi-line-input"
                className="block text-sm font-medium leading-6 text-gray-900"
              >
                Text to Exclude
              </label>
              <textarea
                id="multi-line-input"
                name="multi-line-input"
                rows="4"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2"
                value={exclusionTextBoxValue}
                onChange={(e) => setExclusionTextBoxValue(e.target.value)}
              />
            </div>
            <div className="mt-5 w-full bg-indigo-100/70 p-5 rounded-xl">
              <div className="w-full">
                <label
                  htmlFor="prompt"
                  className="block text-sm font-bold leading-6 text-gray-900"
                >
                  Prompt
                </label>
                <Select
                  id="prompt"
                  name="prompt"
                  options={promptsList}
                  isLoading={isPromptsLoading}
                  value={prompt}
                  onChange={setPrompt}
                  getOptionLabel={getOptionLabel}
                  getOptionValue={getOptionValue}
                  className="mt-1"
                />
              </div>
              <div className="mt-5 w-full p-3 rounded-xl bg-gray-100 font-mono text-xs">
                <span
                  dangerouslySetInnerHTML={{ __html: prompt?.prompt_text }}
                />
              </div>
            </div>
          </div>

          <div className="mt-5 flex items-center justify-end gap-x-6">
            <button
              type="submit"
              className="rounded-md bg-indigo-600 px-10 py-4 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
              disabled={!fileToUpload || uploadIsLoading}
            >
              {uploadIsLoading ? (
                <div className="flex justify-center">
                  <svg
                    aria-hidden="true"
                    className="w-5 h-5 text-gray-200 animate-spin fill-indigo-600"
                    viewBox="0 0 100 101"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z"
                      fill="currentColor"
                    />
                    <path
                      d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z"
                      fill="currentFill"
                    />
                  </svg>
                </div>
              ) : (
                "Upload"
              )}
            </button>
          </div>
        </form>
      </div>
    </>
  );
}
