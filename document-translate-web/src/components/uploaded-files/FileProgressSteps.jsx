import React from "react";
import {
  ArrowDownCircleIcon,
  ArrowUpTrayIcon,
  DocumentMagnifyingGlassIcon,
  LanguageIcon,
  PencilIcon,
} from "@heroicons/react/24/solid";
import "./UploadedFiles.css";
import {
  getFileUrlByStatus,
  getProgressColor,
  isFileProcessed,
  isFileTranslated,
  isFileWatermarked,
} from "../../helpers/fileHelpers";
import { StatusWords } from "../../constants/fileStatusConstants";
import { TooltipWrapper } from "../ui-components/tooltip/TooltipWrapper";

export default function FileProgressSteps({ file }) {
  return (
    <div className="flex w-full md:w-[350px] md:min-w-[350px]">
      <ol className="flex items-center w-full">
        <li
          className={`group flex w-full items-center after:content-[''] after after:w-full after:h-1 after:border-b ${getProgressColor(
            file,
            StatusWords.UPLOADED,
            true
          )} after:border-4 after:inline-block`}
        >
          <div className="flex flex-col relative">
            <span
              className={`relative flex items-center justify-center ${getProgressColor(
                file,
                StatusWords.UPLOADED
              )} rounded-full h-7 w-7 shrink-0`}
            >
              <ArrowUpTrayIcon className="text-white w-4 h-4" />
              <a
                target="_blank"
                href={getFileUrlByStatus(file, StatusWords.UPLOADED)}
                rel="noreferrer"
              >
                <ArrowDownCircleIcon
                  className="absolute left-0 top-0 cursor-pointer text-white w-full h-full  hidden group-hover:block rounded-full bg-emerald-500"
                  title="Download source file"
                />
              </a>
            </span>
            <TooltipWrapper>Uploaded</TooltipWrapper>
          </div>
        </li>
        <li
          className={`group flex w-full items-center after:content-[''] after:w-full after:h-1 after:border-b ${getProgressColor(
            file,
            StatusWords.PROCESSED,
            true
          )} after:border-4 after:inline-block`}
        >
          <div className="flex flex-col relative">
            <span
              className={`relative flex items-center justify-center ${getProgressColor(
                file,
                StatusWords.PROCESSED
              )} rounded-full h-7 w-7 shrink-0`}
            >
              <DocumentMagnifyingGlassIcon className="text-white w-4 h-4" />
              {isFileProcessed(file) && <a
                target="_blank"
                href={getFileUrlByStatus(file, StatusWords.PROCESSED)}
                rel="noreferrer"
              >
                <ArrowDownCircleIcon
                  className="absolute left-0 top-0 cursor-pointer text-white w-full h-full hidden group-hover:block rounded-full bg-emerald-500"
                  title="Download processed file"
                />
              </a>}
            </span>
            <TooltipWrapper>Processed</TooltipWrapper>
          </div>
        </li>
        <li
          className={`group flex w-full items-center after:content-[''] after:w-full after:h-1 after:border-b ${getProgressColor(
            file,
            StatusWords.TRANSLATED,
            true
          )} after:border-4 after:inline-block`}
        >
          <div className="flex flex-col relative">
            <span
              className={`relative flex items-center justify-center ${getProgressColor(
                file,
                StatusWords.TRANSLATED
              )} rounded-full h-7 w-7 shrink-0`}
            >
              <LanguageIcon className="text-white w-4 h-4" />
              {isFileTranslated(file) &&<a
                target="_blank"
                href={getFileUrlByStatus(file, StatusWords.TRANSLATED)}
                rel="noreferrer"
              >
                <ArrowDownCircleIcon
                  className="absolute left-0 top-0 cursor-pointer text-white w-full h-full  hidden group-hover:block rounded-full bg-emerald-500"
                  title="Download translated file"
                />
              </a>}
            </span>
            <TooltipWrapper>Translated</TooltipWrapper>
          </div>
        </li>
        <li className="group flex items-center w-auto">
          <div className="flex flex-col relative">
            <span
              className={`relative flex items-center justify-center ${getProgressColor(
                file,
                StatusWords.WATERMARKED
              )} rounded-full h-7 w-7 shrink-0`}
            >
              <PencilIcon className="text-white w-4 h-4" />
              {isFileWatermarked(file) && <a
                target="_blank"
                href={getFileUrlByStatus(file, StatusWords.WATERMARKED)}
                rel="noreferrer"
              >
                <ArrowDownCircleIcon
                  className="absolute left-0 top-0 cursor-pointer text-white w-full h-full  hidden group-hover:block rounded-full bg-emerald-500"
                  title="Download watermarked file"
                />
              </a>}
            </span>
            <TooltipWrapper>Watermarked</TooltipWrapper>
          </div>
        </li>
      </ol>
    </div>
  );
}
