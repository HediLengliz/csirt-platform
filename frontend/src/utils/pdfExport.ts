// Utility function for PDF export
export function exportToPDF(content: HTMLElement, filename: string) {
  // Create a new window for printing
  const printWindow = window.open('', '_blank')
  if (!printWindow) {
    throw new Error('Unable to open print window. Please allow popups.')
  }

  // Get the content HTML
  const contentHTML = content.innerHTML

  // Create the PDF document HTML
  const pdfHTML = `
    <!DOCTYPE html>
    <html>
      <head>
        <title>${filename}</title>
        <style>
          @media print {
            @page {
              margin: 20mm;
            }
            body {
              font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
              color: #000;
              background: #fff;
            }
            .no-print {
              display: none;
            }
          }
          body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            color: #000;
            background: #fff;
            padding: 20px;
            line-height: 1.6;
          }
          h1 {
            color: #1e293b;
            border-bottom: 3px solid #3b82f6;
            padding-bottom: 10px;
            margin-bottom: 20px;
          }
          h2 {
            color: #334155;
            margin-top: 30px;
            margin-bottom: 15px;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 8px;
          }
          .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
            margin: 2px;
          }
          .badge-critical {
            background: #fee2e2;
            color: #991b1b;
          }
          .badge-high {
            background: #fed7aa;
            color: #9a3412;
          }
          .badge-medium {
            background: #fef3c7;
            color: #92400e;
          }
          .badge-low {
            background: #dbeafe;
            color: #1e40af;
          }
          .info-row {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #e2e8f0;
          }
          .info-label {
            font-weight: 600;
            color: #64748b;
          }
          .info-value {
            color: #1e293b;
          }
          table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
          }
          th, td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #e2e8f0;
          }
          th {
            background: #f1f5f9;
            font-weight: 600;
            color: #475569;
          }
        </style>
      </head>
      <body>
        ${contentHTML}
      </body>
    </html>
  `

  printWindow.document.write(pdfHTML)
  printWindow.document.close()

  // Wait for content to load, then trigger print
  printWindow.onload = () => {
    setTimeout(() => {
      printWindow.print()
      // Close window after print dialog is closed
      printWindow.onafterprint = () => {
        printWindow.close()
      }
    }, 250)
  }
}

