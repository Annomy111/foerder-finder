import {
  Document,
  Packer,
  Paragraph,
  TextRun,
  HeadingLevel,
  AlignmentType,
  UnderlineType,
  BorderStyle,
} from 'docx'
import { saveAs } from 'file-saver'

/**
 * Export funding opportunity details to a DOCX file
 * @param {Object} funding - The funding opportunity object
 */
export async function exportFundingToDocx(funding) {
  const children = []

  // Title
  children.push(
    new Paragraph({
      text: funding.title,
      heading: HeadingLevel.HEADING_1,
      alignment: AlignmentType.CENTER,
      spacing: { after: 400 },
    })
  )

  // Provider
  children.push(
    new Paragraph({
      children: [
        new TextRun({
          text: 'Fördergeber: ',
          bold: true,
        }),
        new TextRun({
          text: funding.provider || 'Keine Angabe',
        }),
      ],
      spacing: { after: 200 },
    })
  )

  // Deadline
  if (funding.deadline) {
    children.push(
      new Paragraph({
        children: [
          new TextRun({
            text: 'Antragsfrist: ',
            bold: true,
          }),
          new TextRun({
            text: new Date(funding.deadline).toLocaleDateString('de-DE', {
              day: '2-digit',
              month: 'long',
              year: 'numeric',
            }),
          }),
        ],
        spacing: { after: 200 },
      })
    )
  }

  // Funding Amount
  if (funding.min_funding_amount || funding.max_funding_amount) {
    const amountText = [
      funding.min_funding_amount
        ? `${funding.min_funding_amount.toLocaleString('de-DE')}€`
        : '',
      funding.min_funding_amount && funding.max_funding_amount ? ' – ' : '',
      funding.max_funding_amount
        ? `${funding.max_funding_amount.toLocaleString('de-DE')}€`
        : '',
    ].join('')

    children.push(
      new Paragraph({
        children: [
          new TextRun({
            text: 'Fördersumme: ',
            bold: true,
          }),
          new TextRun({
            text: amountText,
          }),
        ],
        spacing: { after: 400 },
      })
    )
  }

  // Separator
  children.push(
    new Paragraph({
      text: '',
      border: {
        bottom: {
          color: '000000',
          space: 1,
          style: BorderStyle.SINGLE,
          size: 6,
        },
      },
      spacing: { after: 400 },
    })
  )

  // Description
  if (funding.cleaned_text) {
    children.push(
      new Paragraph({
        text: 'Programmbeschreibung',
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 400, after: 200 },
      })
    )
    children.push(
      new Paragraph({
        text: funding.cleaned_text.substring(0, 2000),
        spacing: { after: 400 },
      })
    )
  }

  // Eligible Costs
  if (funding.eligible_costs && funding.eligible_costs.length > 0) {
    children.push(
      new Paragraph({
        text: 'Was wird gefördert?',
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 400, after: 200 },
      })
    )
    funding.eligible_costs.forEach((cost) => {
      children.push(
        new Paragraph({
          text: `• ${cost}`,
          spacing: { after: 100 },
        })
      )
    })
    children.push(
      new Paragraph({
        text: '',
        spacing: { after: 400 },
      })
    )
  }

  // Eligibility
  if (funding.eligibility && funding.eligibility.length > 0) {
    children.push(
      new Paragraph({
        text: 'Fördervoraussetzungen',
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 400, after: 200 },
      })
    )
    funding.eligibility.forEach((criterion) => {
      children.push(
        new Paragraph({
          text: `• ${criterion}`,
          spacing: { after: 100 },
        })
      )
    })
    children.push(
      new Paragraph({
        text: '',
        spacing: { after: 400 },
      })
    )
  }

  // Target Groups
  if (funding.target_groups && funding.target_groups.length > 0) {
    children.push(
      new Paragraph({
        text: 'Zielgruppen',
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 400, after: 200 },
      })
    )
    funding.target_groups.forEach((group) => {
      children.push(
        new Paragraph({
          text: `• ${group}`,
          spacing: { after: 100 },
        })
      )
    })
    children.push(
      new Paragraph({
        text: '',
        spacing: { after: 400 },
      })
    )
  }

  // Requirements
  if (funding.requirements && funding.requirements.length > 0) {
    children.push(
      new Paragraph({
        text: 'Erforderliche Nachweise',
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 400, after: 200 },
      })
    )
    funding.requirements.forEach((req) => {
      children.push(
        new Paragraph({
          text: `• ${req}`,
          spacing: { after: 100 },
        })
      )
    })
    children.push(
      new Paragraph({
        text: '',
        spacing: { after: 400 },
      })
    )
  }

  // Evaluation Criteria
  if (funding.evaluation_criteria && funding.evaluation_criteria.length > 0) {
    children.push(
      new Paragraph({
        text: 'Bewertungskriterien',
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 400, after: 200 },
      })
    )
    funding.evaluation_criteria.forEach((criterion) => {
      children.push(
        new Paragraph({
          text: `• ${criterion}`,
          spacing: { after: 100 },
        })
      )
    })
    children.push(
      new Paragraph({
        text: '',
        spacing: { after: 400 },
      })
    )
  }

  // Application Process
  if (funding.application_process) {
    children.push(
      new Paragraph({
        text: 'Antragsverfahren',
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 400, after: 200 },
      })
    )
    children.push(
      new Paragraph({
        text: funding.application_process,
        spacing: { after: 400 },
      })
    )
  }

  // Contact & Source
  if (funding.contact_person || funding.source_url) {
    children.push(
      new Paragraph({
        text: 'Kontakt & Weitere Informationen',
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 400, after: 200 },
      })
    )

    if (funding.contact_person) {
      children.push(
        new Paragraph({
          children: [
            new TextRun({
              text: 'Ansprechpartner: ',
              bold: true,
            }),
            new TextRun({
              text: funding.contact_person,
            }),
          ],
          spacing: { after: 100 },
        })
      )
    }

    if (funding.source_url) {
      children.push(
        new Paragraph({
          children: [
            new TextRun({
              text: 'Offizielle Quelle: ',
              bold: true,
            }),
            new TextRun({
              text: funding.source_url,
              style: 'Hyperlink',
              underline: {
                type: UnderlineType.SINGLE,
                color: '0000FF',
              },
            }),
          ],
          spacing: { after: 100 },
        })
      )
    }
  }

  // Footer
  children.push(
    new Paragraph({
      text: '',
      spacing: { before: 600 },
      border: {
        top: {
          color: '000000',
          space: 1,
          style: BorderStyle.SINGLE,
          size: 6,
        },
      },
    })
  )
  children.push(
    new Paragraph({
      children: [
        new TextRun({
          text: 'Exportiert von EduFunds • ',
          size: 18,
        }),
        new TextRun({
          text: new Date().toLocaleDateString('de-DE'),
          size: 18,
        }),
      ],
      alignment: AlignmentType.CENTER,
      spacing: { before: 200 },
    })
  )

  // Create document
  const doc = new Document({
    sections: [
      {
        properties: {},
        children,
      },
    ],
  })

  // Generate and save
  const blob = await Packer.toBlob(doc)
  const filename = `${funding.title.replace(/[^a-zA-Z0-9äöüÄÖÜß\s-]/g, '')
    .trim()
    .substring(0, 50)}.docx`
  saveAs(blob, filename)
}
