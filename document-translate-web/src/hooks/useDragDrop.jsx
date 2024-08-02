import { useCallback, useRef } from "react";

export const useDragDrop = ({ setFileToUpload }) => {
  const wrapperRef = useRef(null);
  const onDragEnter = useCallback((event) => {
    event.preventDefault();
    wrapperRef.current.classList.add("dragover");
  }, []);
  const onDragLeave = useCallback((event) => {
    event.preventDefault();
    wrapperRef.current.classList.remove("dragover");
  }, []);
  const onDrop = useCallback(
    (event) => {
      event.preventDefault();
      event.stopPropagation();
      const droppedFiles = event.dataTransfer.files;
      if (droppedFiles.length > 0) {
        const newFile = Array.from(droppedFiles)[0];
        setFileToUpload(newFile);
      }
      wrapperRef.current.classList.remove("dragover");
    },
    [setFileToUpload]
  );

  const handleRemoveFile = useCallback(() => {
    setFileToUpload(null);
  }, [setFileToUpload]);

  const handleFileChange = useCallback(
    (event) => {
      const selectedFiles = event.target.files;
      if (selectedFiles && selectedFiles.length > 0) {
        const newFile = Array.from(selectedFiles)[0];
        setFileToUpload(newFile);
      }
    },
    [setFileToUpload]
  );

  return {
    wrapperRef,
    onDragEnter,
    onDragLeave,
    onDrop,
    handleRemoveFile,
    handleFileChange,
  };
};
