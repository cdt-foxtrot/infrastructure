using Microsoft.Xna.Framework.Graphics;
using System.Collections.Generic;
using Microsoft.Xna.Framework;
using System.Diagnostics;

namespace Scoreboard
{
    /// <summary>
    /// Health bar for a box in the competition.
    /// </summary>
    public class HealthBar
    {

        // Fields:
        private int m_dHealth;
        private List<ResponsiveUIElement> m_lHearts;
        private Texture2D m_pFullHeart;
        private Texture2D m_pHalfHeart;
        private Vector2 m_v2Percent;

        // Properties:
        /// <summary>
        /// Get/Sets the health of this bar.
        /// </summary>
        public int Health 
        { 
            get { return m_dHealth; } 
            set { m_dHealth = value; } 
        }

        // Constructors:
        /// <summary>
        /// Parameterized constructor for the HealthBar.
        /// </summary>
        /// <param name="a_pFullHeart">Full heart texture.</param>
        /// <param name="a_pHalfHeart">Half heart texture.</param>
        /// <param name="a_v2StartingPosition">Starting position of the health bar.</param>
        /// <param name="a_v2StartingPercent">Percent scaling for the health bar.</param>
        public HealthBar(Texture2D a_pFullHeart, Texture2D a_pHalfHeart, Vector2 a_v2StartingPosition, Vector2 a_v2StartingPercent)
        {
            m_dHealth = 20;

            m_pFullHeart = a_pFullHeart;
            m_pHalfHeart = a_pHalfHeart;

            m_lHearts = new List<ResponsiveUIElement>();
            for (uint i = 0; i < m_dHealth / 2; i++)
            {
                m_lHearts.Add(new ResponsiveUIElement(a_pFullHeart, a_v2StartingPosition));
                a_v2StartingPosition.X += 30;
            }

            m_v2Percent = a_v2StartingPercent;
        }

        // Methods:
        /// <summary>
        /// Resizes all portions of the HealthBar appropriately.
        /// </summary>
        /// <param name="a_pGraphics">Graphics device used for getting the viewport.</param>
        public void OnResize(GraphicsDeviceManager a_pGraphics)
        {
            // Initial position of the first heart.
            Vector2 v2Position = m_lHearts[0].Position;

            // Looping through the hearts.
            foreach(ResponsiveUIElement element in m_lHearts)
            {
                // Resizing them appropriately.
                element.OnResize(a_pGraphics, m_v2Percent, v2Position);

                // Calculating the proper positions.
                v2Position.X += 20.0f * (m_v2Percent.X + 1.75f);
            }
        }

        /// <summary>
        /// Renders everything for the health to the window.
        /// </summary>
        /// <param name="a_pSpriteBatch">SpriteBatch used for rendering </param>
        public void Draw(SpriteBatch a_pSpriteBatch)
        {
            // If there is an even amount of health,
            if (m_dHealth % 2 == 0)
            {
                // Draw all of the hearts as normal.
                for (int i = 0; i < m_lHearts.Count; i++)
                {
                    if (i < m_dHealth / 2)
                    {
                        m_lHearts[i].Draw(a_pSpriteBatch);
                    }
                    else
                    {
                        m_lHearts[i].Draw(a_pSpriteBatch, Color.DarkSlateGray);
                    }
                }
            }
            // Otherwise,
            else
            {
                // Render the last heart differently.
                for (int i = 0; i < m_lHearts.Count; i++)
                {
                    // On the last iteration, change the texture.
                    if (i == (m_dHealth / 2))
                    {
                        m_lHearts[i].Texture = m_pHalfHeart;
                    }

                    // Making sure only the full hearts are rendered red.
                    if (i < m_dHealth / 2 + 1)
                    {
                        m_lHearts[i].Draw(a_pSpriteBatch);
                    }
                    // The rest are faded out and tinted gray.
                    else
                    {
                        m_lHearts[i].Draw(a_pSpriteBatch, Color.DarkSlateGray);
                    }

                    // Return the texture to normal.
                    if (i == (m_dHealth / 2))
                    {
                        m_lHearts[i].Texture = m_pFullHeart;
                    }
                }
            }
        }
    }
}
