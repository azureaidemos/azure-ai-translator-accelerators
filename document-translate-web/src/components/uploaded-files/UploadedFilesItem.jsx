import React from "react";
import "./UploadedFiles.css";
import { Statuses } from "../../constants/fileStatusConstants";
import {
  dateTimeFormat,
  getFileStatus,
  getFileUrl,
} from "../../helpers/fileHelpers";
import FileProgressSteps from "./FileProgressSteps.jsx";
import { TooltipWrapper } from "../ui-components/tooltip/TooltipWrapper.jsx";
import { useCallback, useState } from "react";
import { ArrowDownIcon, ArrowUpIcon } from "@heroicons/react/24/outline";
import { getLanguageByCode } from "../../helpers/languageHelpers.js";

export default function UploadedFilesItem({ file }) {
  const { bgColor, fgColor, statusName } = Statuses[getFileStatus(file)];
  const [isGlossaryContentShown, setIsGlossaryContentShown] = useState(false);
  const [isExcludedTextShown, setIsExcludedTextShown] = useState(false);
  const toggleGlossaryContent = useCallback(() => {
    setIsGlossaryContentShown((currentValue) => !currentValue);
  }, [setIsGlossaryContentShown]);

  const toggleExcludedText = useCallback(() => {
    setIsExcludedTextShown((currentValue) => !currentValue);
  }, [setIsExcludedTextShown]);

  return (
    <li>
      <div className="flex flex-col md:flex-row justify-between items-start gap-x-6 gap-y-3 pt-5 md:pb-0">
        <div className="flex min-w-0 gap-x-4">
          <div className="min-w-0 flex-auto">
            <div className="text-sm font-semibold leading-6 text-gray-900 flex items-center">
              <div className="group h-3.5 w-3.5 mr-2 relative">
                {!getFileStatus(file) && (
                  <svg
                    aria-hidden="true"
                    className="w-5 h-5 text-gray-200 animate-spin fill-indigo-600 absolute top-[-3px] left-[-3px]"
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
                )}
                <div className={`h-3.5 w-3.5 rounded-full ${bgColor} p-1`}>
                  <div className={`h-1.5 w-1.5 rounded-full ${fgColor}`} />
                </div>
                <TooltipWrapper>{statusName}</TooltipWrapper>
              </div>
              <a
                className="truncate text-ellipsis mr-4"
                href={getFileUrl(file)}
                alt={file.file_name}
              >
                {file.file_name}
              </a>
            </div>
            <p className="ml-6 text-xs leading-5 text-gray-500">
              <time dateTime={dateTimeFormat(file.upload_datetime)}>
                {dateTimeFormat(file.upload_datetime)}
              </time>
            </p>
          </div>
        </div>
        <div className="flex flex-col items-end">
          <div className="text-xs mb-3 px-3 py-1 border-l-4 border-gray-200 bg-gray-200 rounded-md">
            {getLanguageByCode(file.fromLanguage) +
              " ➜  " +
              getLanguageByCode(file.toLanguage)}
          </div>
          <FileProgressSteps file={file} />
        </div>
      </div>
      <div className="flex gap-5 mt-4 p-4 rounded-md bg-gray-200/50">
        <div className="w-full sm:w-auto sm:flex-1">
          {!!file.glossary_content && (
            <>
              <button
                className="flex justify-center text-indigo-900 text-sm"
                onClick={toggleGlossaryContent}
              >
                {isGlossaryContentShown ? (
                  <>
                    Hide Glossary content{" "}
                    <ArrowUpIcon className="ml-1 w-4 h-4" />
                  </>
                ) : (
                  <>
                    Show Glossary content{" "}
                    <ArrowDownIcon className="ml-1 w-4 h-4" />
                  </>
                )}
              </button>
              {isGlossaryContentShown && (
                <div className="flex gap-1 w-full bg-gray-300/50 p-5 rounded-md mt-5 flex-wrap">
                  {JSON.parse(file.glossary_content)?.map(
                    ({ items: glossary }) => (
                      <span className="inline-block text-sm bg-white rounded-md py-1 px-2">
                        {glossary}
                      </span>
                    )
                  )}
                </div>
              )}
            </>
          )}
        </div>
        <div className="w-full sm:w-auto sm:flex-1">
          {!!file.exclusion_text && (
            <>
              <button
                className="flex justify-center text-indigo-900 text-sm"
                onClick={toggleExcludedText}
              >
                {isExcludedTextShown ? (
                  <>
                    Hide Excluded text <ArrowUpIcon className="ml-1 w-4 h-4" />
                  </>
                ) : (
                  <>
                    Show Excluded text{" "}
                    <ArrowDownIcon className="ml-1 w-4 h-4" />
                  </>
                )}
              </button>
              {isExcludedTextShown && (
                <div className="flex gap-1 w-full bg-gray-300/50 p-5 rounded-md mt-5">
                  <span className="inline-block text-sm bg-white rounded-md py-1 px-2">
                    {file.exclusion_text}
                  </span>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </li>
  );
}
