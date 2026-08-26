import {
  Download,
  FileText,
  Image,
  Trash2,
  Upload,
  Video,
  X,
} from "lucide-react"

import {
  useState,
} from "react"

import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query"

import {
  deleteTradeAttachment,
  fetchTradeAttachmentBlob,
  fetchTradeAttachments,
  uploadTradeAttachment,
} from "@/api/tradeAttachments"

import type {
  Trade,
} from "@/types/trade"

import type {
  TradeAttachment,
  TradeAttachmentStage,
} from "@/types/tradeAttachment"


function fileSize(
  bytes: number,
) {
  if (
    bytes < 1024
  ) {
    return `${bytes} B`
  }

  if (
    bytes <
    1024 * 1024
  ) {
    return `${(
      bytes /
      1024
    ).toFixed(1)} KB`
  }

  return `${(
    bytes /
    1024 /
    1024
  ).toFixed(1)} MB`
}


function AttachmentIcon({
  type,
}: {
  type: string
}) {
  if (
    type === "image"
  ) {
    return (
      <Image className="size-5" />
    )
  }

  if (
    type === "video"
  ) {
    return (
      <Video className="size-5" />
    )
  }

  return (
    <FileText className="size-5" />
  )
}


async function openAttachment(
  tradeId: number,
  attachment:
    TradeAttachment,
) {
  const blob =
    await fetchTradeAttachmentBlob(
      tradeId,
      attachment.id,
    )

  const url =
    URL.createObjectURL(
      blob,
    )

  window.open(
    url,
    "_blank",
    "noopener,noreferrer",
  )

  setTimeout(
    () =>
      URL.revokeObjectURL(
        url,
      ),
    60_000,
  )
}


export default function TradeMediaPanel({
  trade,
  onClose,
}: {
  trade: Trade
  onClose: () => void
}) {
  const queryClient =
    useQueryClient()

  const [
    stage,
    setStage,
  ] = useState<TradeAttachmentStage>(
    "before",
  )

  const [
    uploadError,
    setUploadError,
  ] = useState("")


  const query =
    useQuery({
      queryKey: [
        "trade-attachments",
        trade.id,
      ],

      queryFn: () =>
        fetchTradeAttachments(
          trade.id,
        ),
    })


  const upload =
    useMutation({
      mutationFn:
        ({
          file,
          stage,
        }: {
          file: File
          stage: TradeAttachmentStage
        }) =>
          uploadTradeAttachment(
            trade.id,
            file,
            stage,
          ),

      onSuccess:
        async () => {
          setUploadError("")

          await queryClient.invalidateQueries({
            queryKey: [
              "trade-attachments",
              trade.id,
            ],
          })
        },

      onError:
        () => {
          setUploadError(
            "Unable to upload this attachment.",
          )
        },
    })


  const remove =
    useMutation({
      mutationFn:
        (
          attachmentId:
            number,
        ) =>
          deleteTradeAttachment(
            trade.id,
            attachmentId,
          ),

      onSuccess:
        async () => {
          await queryClient.invalidateQueries({
            queryKey: [
              "trade-attachments",
              trade.id,
            ],
          })
        },
    })


  const attachments =
    query.data
      ?.attachments ||
    []


  return (
    <div className="fixed inset-0 z-[70] flex justify-end bg-black/70 backdrop-blur-sm">

      <aside className="h-full w-full max-w-2xl overflow-y-auto border-l border-white/10 bg-[#080d17] p-6 sm:p-8">

        <div className="flex items-start justify-between gap-5">

          <div>

            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-blue-300">
              Trade Evidence
            </p>

            <h2 className="mt-2 text-2xl font-semibold">
              {trade.pair} Media
            </h2>

            <p className="mt-2 text-sm text-slate-400">
              Save chart screenshots, strategy references,
              PDFs and short recordings with this trade.
            </p>

          </div>


          <button
            type="button"
            onClick={
              onClose
            }
            className="grid size-10 shrink-0 place-items-center rounded-2xl border border-white/10 bg-white/[0.03]"
          >
            <X className="size-5" />
          </button>

        </div>


        <section className="mt-7 rounded-3xl border border-blue-400/10 bg-blue-400/[0.04] p-5">

          <label className="text-sm font-medium">
            Attachment stage
          </label>

          <select
            value={
              stage
            }
            onChange={(
              event,
            ) =>
              setStage(
                event.target.value as TradeAttachmentStage,
              )
            }
            className="mt-3 w-full rounded-2xl border border-white/10 bg-[#0b1120] px-4 py-3"
          >
            <option value="before">
              Before trade
            </option>

            <option value="after">
              After trade
            </option>

            <option value="strategy">
              Strategy reference
            </option>

            <option value="general">
              General
            </option>
          </select>


          <label className="mt-4 flex cursor-pointer items-center justify-center gap-2 rounded-2xl border border-dashed border-blue-400/30 bg-blue-400/[0.04] px-5 py-8 text-blue-300 transition hover:bg-blue-400/[0.08]">

            <Upload className="size-5" />

            {upload.isPending
              ? "Uploading..."
              : "Upload screenshot, PDF or video"}

            <input
              type="file"
              className="hidden"
              accept="image/png,image/jpeg,image/webp,application/pdf,video/mp4,video/webm,video/quicktime"
              disabled={
                upload.isPending
              }
              onChange={(
                event,
              ) => {
                const file =
                  event.target
                    .files?.[0]

                if (
                  file
                ) {
                  upload.mutate({
                    file,
                    stage,
                  })
                }

                event.currentTarget.value =
                  ""
              }}
            />

          </label>


          {uploadError && (
            <p className="mt-3 text-sm text-red-300">
              {uploadError}
            </p>
          )}

        </section>


        <section className="mt-8">

          <div className="flex items-center justify-between">

            <h3 className="text-lg font-semibold">
              Attachments
            </h3>

            <span className="rounded-full bg-white/[0.04] px-3 py-1 text-xs text-slate-400">
              {attachments.length}
            </span>

          </div>


          {query.isLoading ? (
            <div className="mt-6 text-sm text-slate-500">
              Loading attachments...
            </div>
          ) : attachments.length ? (
            <div className="mt-4 space-y-3">

              {attachments.map(
                (
                  attachment,
                ) => (
                  <article
                    key={
                      attachment.id
                    }
                    className="flex items-center justify-between gap-4 rounded-3xl border border-white/[0.07] bg-white/[0.025] p-4"
                  >

                    <div className="flex min-w-0 items-center gap-4">

                      <div className="grid size-11 shrink-0 place-items-center rounded-2xl bg-blue-400/10 text-blue-300">

                        <AttachmentIcon
                          type={
                            attachment.attachment_type
                          }
                        />

                      </div>


                      <div className="min-w-0">

                        <p className="truncate font-medium">
                          {attachment.original_name}
                        </p>

                        <p className="mt-1 text-xs text-slate-500">
                          {attachment.stage} ·{" "}
                          {fileSize(
                            attachment.file_size,
                          )}
                        </p>

                      </div>

                    </div>


                    <div className="flex shrink-0 gap-2">

                      <button
                        type="button"
                        title="Open"
                        onClick={() =>
                          openAttachment(
                            trade.id,
                            attachment,
                          )
                        }
                        className="grid size-9 place-items-center rounded-xl bg-blue-400/10 text-blue-300"
                      >
                        <Download className="size-4" />
                      </button>


                      <button
                        type="button"
                        title="Delete"
                        onClick={() => {
                          if (
                            window.confirm(
                              "Delete this attachment?",
                            )
                          ) {
                            remove.mutate(
                              attachment.id,
                            )
                          }
                        }}
                        className="grid size-9 place-items-center rounded-xl bg-red-400/10 text-red-300"
                      >
                        <Trash2 className="size-4" />
                      </button>

                    </div>

                  </article>
                ),
              )}

            </div>
          ) : (
            <div className="mt-5 rounded-3xl border border-dashed border-white/10 p-10 text-center text-sm text-slate-500">
              No trade media uploaded yet.
            </div>
          )}

        </section>

      </aside>

    </div>
  )
}
