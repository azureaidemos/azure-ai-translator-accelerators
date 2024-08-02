import {
  StatusWords,
  Statuses,
  progressStepToPropMap,
  statusWordToValueMap,
} from "../constants/fileStatusConstants";

export const dateTimeFormat = (dateTime) =>
  Intl.DateTimeFormat("en-US", {
    day: "numeric",
    month: "long",
    year: "numeric",
    hour: "numeric",
    minute: "numeric",
    second: "numeric",
  }).format(new Date(dateTime));

export const getFileUrl = (file) =>
  file.watermark_zone_path || file.translated_zone_path || file.landing_zone_path;

export const getFileUrlByStatus = (file, status) => ({
    [StatusWords.UPLOADED]: file.landing_zone_path,
    [StatusWords.PROCESSED]: file.glossary_zone_path,
    [StatusWords.TRANSLATED]: file.translated_zone_path,
    [StatusWords.WATERMARKED]: file.watermark_zone_path,
  }[status])

export const isFileProcessed = (file) => file.glossary_processing_status === "done"
export const isFileTranslated = (file) => file.translation_status === "done"
export const isFileWatermarked = (file) => file.watermark_status === "done"

export const getFileStatus = (file) => {
  if (
    [
      file.upload_status,
      file.glossary_processing_status,
      file.translation_status,
      file.watermark_status,
    ].includes("failed")
  )
    return 2; // Failed
  if (
    ![
      file.upload_status,
      file.glossary_processing_status,
      file.translation_status,
      file.watermark_status,
    ].every(Boolean)
  )
    return 0; // In progress, some still are null
  else return 1; // Success
};

export const getProgressColor = (file, step, isAfter = false) => {
  const statusKey = statusWordToValueMap[file[progressStepToPropMap[step]]] || 0; // Default to 0 if undefined
  const status = Statuses[statusKey] || Statuses[2]; // Default to Statuses[0] if undefined
  return status[isAfter ? "afterColor" : "fgColor"];
};
