export type TradeAttachmentStage =
  | "general"
  | "before"
  | "after"
  | "strategy"

export type TradeAttachmentType =
  | "image"
  | "pdf"
  | "video"

export type TradeAttachment = {
  id: number
  user_id: number
  trade_id: number

  attachment_type:
    TradeAttachmentType

  stage:
    TradeAttachmentStage

  original_name: string
  stored_name: string

  mime_type?: string | null
  file_size: number

  created_at: string
}

export type TradeAttachmentListResponse = {
  total: number
  attachments: TradeAttachment[]
}
