import {
  useRef,
} from "react";


function DocumentLibrary({
  documents,
  uploading,
  deletingDocumentId,
  error,
  onUploadDocuments,
  onDeleteDocument,
}) {
  const fileInputRef =
    useRef(null);


  // ============================================================
  // Open File Picker
  // ============================================================

  function openFilePicker() {
    if (
      uploading ||
      deletingDocumentId
    ) {
      return;
    }


    fileInputRef
      .current
      ?.click();
  }


  // ============================================================
  // File Selected
  // ============================================================

  function handleFileChange(
    event
  ) {
    const files =
      Array.from(
        event.target.files ||
        []
      );


    /*
     * 清空 input，
     * 允许之后再次选择相同文件。
     */
    event.target.value =
      "";


    if (
      files.length === 0
    ) {
      return;
    }


    onUploadDocuments(
      files
    );
  }


  // ============================================================
  // Delete
  // ============================================================

  function handleDelete(
    document
  ) {
    const filename =
      document.filename ||
      "该文档";


    const confirmed =
      window.confirm(
        (
          `确定删除「${filename}」吗？`
          + "\n\n"
          + "删除后，该文档将不再参与之后的研究检索。"
        )
      );


    if (!confirmed) {
      return;
    }


    console.log(
      "[DocumentLibrary] Confirmed delete:",
      document
    );


    if (
      typeof onDeleteDocument !==
      "function"
    ) {
      console.error(
        "[DocumentLibrary] "
        + "onDeleteDocument is not connected."
      );

      return;
    }


    onDeleteDocument(
      document
    );
  }


  // ============================================================
  // Render
  // ============================================================

  return (
    <section className="document-library">

      {/* ======================================================
          Header
      ======================================================= */}

      <div className="document-library-header">

        <span className="sidebar-section-title">
          文档库
        </span>


        <span className="document-count">
          {documents.length}
        </span>

      </div>


      {/* ======================================================
          Documents
      ======================================================= */}

      <div className="document-list">

        {documents.length > 0 ? (
          documents.map(
            (document) => {
              const documentId =
                document.document_id ||
                document.id;


              const deleting =
                (
                  deletingDocumentId ===
                  documentId
                );


              return (
                <DocumentItem
                  key={
                    documentId ||
                    document.filename
                  }

                  document={
                    document
                  }

                  deleting={
                    deleting
                  }

                  deleteDisabled={
                    Boolean(
                      deletingDocumentId
                    )
                  }

                  onDelete={() =>
                    handleDelete(
                      document
                    )
                  }
                />
              );
            }
          )
        ) : (
          <div className="document-empty">

            <span>
              暂无文档
            </span>

            <small>
              上传 PDF 后可在所有研究对话中使用
            </small>

          </div>
        )}

      </div>


      {/* ======================================================
          Error
      ======================================================= */}

      {error && (
        <div className="document-error">
          {error}
        </div>
      )}


      {/* ======================================================
          Hidden Input
      ======================================================= */}

      <input
        ref={
          fileInputRef
        }

        type="file"

        accept=".pdf,application/pdf"

        multiple

        className="document-file-input"

        onChange={
          handleFileChange
        }
      />


      {/* ======================================================
          Upload
      ======================================================= */}

      <button
        type="button"

        className="document-upload-button"

        disabled={
          uploading ||
          Boolean(
            deletingDocumentId
          )
        }

        onClick={
          openFilePicker
        }
      >

        <span className="document-upload-icon">
          +
        </span>


        <span>
          {uploading
            ? "正在处理文档..."
            : (
                deletingDocumentId
                  ? "正在更新文档库..."
                  : "上传 PDF"
              )}
        </span>

      </button>

    </section>
  );
}


// ============================================================
// Document Item
// ============================================================


function DocumentItem({
  document,
  deleting,
  deleteDisabled,
  onDelete,
}) {
  const status =
    document.status ||
    "ready";


  const filename =
    document.filename ||
    document.name ||
    "未命名文档";


  const pages =
    document.pages ??
    document.page_count ??
    null;


  const chunks =
    document.chunks ??
    document.chunk_count ??
    null;


  return (
    <div
      className={
        deleting
          ? (
              "document-item "
              + "deleting"
            )
          : "document-item"
      }
    >

      <div className="document-icon">
        PDF
      </div>


      <div className="document-item-content">

        <div
          className="document-name"
          title={filename}
        >
          {filename}
        </div>


        <div className="document-meta">

          <span
            className={
              `document-status ${status}`
            }
          >
            {deleting
              ? "正在删除..."
              : formatStatus(
                  status
                )}
          </span>


          {!deleting &&
            pages != null && (
              <span>
                {pages} 页
              </span>
            )}


          {!deleting &&
            chunks != null && (
              <span>
                {chunks} 个片段
              </span>
            )}

        </div>

      </div>


      {/* ====================================================
          Delete
      ===================================================== */}

      <button
        type="button"

        className="document-delete-button"

        disabled={
          deleting ||
          deleteDisabled
        }

        title={
          deleting
            ? "正在删除"
            : "删除文档"
        }

        aria-label={
          `删除 ${filename}`
        }

        onClick={
          onDelete
        }
      >
        {deleting
          ? "…"
          : "×"}
      </button>

    </div>
  );
}


// ============================================================
// Status
// ============================================================


function formatStatus(
  value
) {
  const labels = {
    ready:
      "可用",

    processing:
      "处理中",

    uploading:
      "上传中",

    failed:
      "失败",

    error:
      "失败",
  };


  return (
    labels[value] ||
    value ||
    "未知"
  );
}


export default DocumentLibrary;