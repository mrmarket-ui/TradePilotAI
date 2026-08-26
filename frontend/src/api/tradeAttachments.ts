import api from "@/api/client"

import type {
  TradeAttachment,
  TradeAttachmentListResponse,
  TradeAttachmentStage,
} from "@/types/tradeAttachment"


export async function fetchTradeAttachments(
  tradeId: number,
): Promise<TradeAttachmentListResponse> {

  const response =
    await api.get<TradeAttachmentListResponse>(
      `/trades/${tradeId}/attachments`,
    )

  return response.data
}


export async function uploadTradeAttachment(
  tradeId: number,
  file: File,
  stage: TradeAttachmentStage,
): Promise<TradeAttachment> {

  const form =
    new FormData()

  form.append(
    "file",
    file,
  )

  form.append(
    "stage",
    stage,
  )

  const response =
    await api.post<TradeAttachment>(
      `/trades/${tradeId}/attachments`,
      form,
      {
        headers: {
          "Content-Type":
            "multipart/form-data",
        },
      },
    )

  return response.data
}


export async function deleteTradeAttachment(
  tradeId: number,
  attachmentId: number,
): Promise<void> {

  await api.delete(
    `/trades/${tradeId}/attachments/${attachmentId}`,
  )
}


export async function fetchTradeAttachmentBlob(
  tradeId: number,
  attachmentId: number,
): Promise<Blob> {

  const response =
    await api.get(
      `/trades/${tradeId}/attachments/${attachmentId}/file`,
      {
        responseType: "blob",
      },
    )

  return response.data
}
