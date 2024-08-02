export const StatusWords = {
  UPLOADED: "uploaded",
  PROCESSED: "processed",
  TRANSLATED: "translated",
  WATERMARKED: "watermarked",
};

export const Statuses = {
  0: {
    statusName: "In Progress",
    bgColor: "bg-gray-400/20",
    fgColor: "bg-gray-400",
    afterColor: "after:border-gray-300",
  },
  1: {
    statusName: "Completed",
    bgColor: "bg-emerald-500/20",
    fgColor: "bg-emerald-500",
    afterColor: "after:border-emerald-400",
  },
  2: {
    statusName: "Failed",
    bgColor: "bg-red-500/20",
    fgColor: "bg-red-500",
  },
};

export const statusWordToValueMap = {
  null: 0,
  done: 1,
  failed: 2
};

export const progressStepToPropMap = {
  [StatusWords.UPLOADED]: "upload_status",
  [StatusWords.PROCESSED]: "glossary_processing_status",
  [StatusWords.TRANSLATED]: "translation_status",
  [StatusWords.WATERMARKED]: "watermark_status",
};
